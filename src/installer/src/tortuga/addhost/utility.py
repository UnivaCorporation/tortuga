# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, Dict

from sqlalchemy.orm.session import Session
from tortuga.config.configManager import ConfigManager
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.exceptions.profileMappingNotAllowed import \
    ProfileMappingNotAllowed
from tortuga.node import node_count_validator
from tortuga.resourceAdapter import resourceAdapterFactory
from cryptography.fernet import Fernet
import json


def validate_addnodes_request(session: Session,
                              addNodesRequest: Dict[str, Any]):
    """
    :raises:
        HardwareProfileNotFound
        SoftwareProfileNotFound
        ProfileMappingNotAllowed
        InvalidArgument
        OperationFailed

    """
    if 'hardwareProfile' not in addNodesRequest and \
            'softwareProfile' not in addNodesRequest:
        raise InvalidArgument(
            'Hardware and/or software profile must be specified')

    hpapi = HardwareProfilesDbHandler()
    spapi = SoftwareProfilesDbHandler()

    hardwareProfileName = addNodesRequest['hardwareProfile'] \
        if 'hardwareProfile' in addNodesRequest else None
    nodeDetails = addNodesRequest.get('nodeDetails', [])
    softwareProfileName = addNodesRequest['softwareProfile'] \
        if 'softwareProfile' in addNodesRequest else None
    nodeCount = int(addNodesRequest.get('count', 0))
    rackNumber = addNodesRequest.get('rack')

    # Look up hardware profile
    hp = hpapi.getHardwareProfile(session, hardwareProfileName) \
        if hardwareProfileName else None

    # Look up software profile
    sp = spapi.getSoftwareProfile(
        session, softwareProfileName) if softwareProfileName else None

    # Make sure that if a software profile is given that it is allowed
    # to be used with the given hardware profile
    if sp is not None and hp is not None:
        checkProfilesMapped(sp, hp)
    elif sp is not None and hp is None:
        if not sp.hardwareprofiles:
            raise InvalidArgument(
                'Software profile [{0}] is not mapped to any hardware'
                ' profiles'.format(softwareProfileName))

        if len(sp.hardwareprofiles) > 1:
            raise InvalidArgument(
                'Ambiguous request: multiple hardware profiles are'
                ' mapped to software profile [{0}]'.format(
                    softwareProfileName))

        hp = sp.hardwareprofiles[0]
    elif hp is not None and sp is None:
        if not hp.mappedsoftwareprofiles:
            raise InvalidArgument(
                'Hardware profile [{0}] is not mapped to any software'
                ' profiles'.format(hardwareProfileName))

        if len(hp.mappedsoftwareprofiles) > 1:
            raise InvalidArgument(
                'Ambiguous request: multiple software profiles are'
                ' mapped to hardware profile [{0}]'.format(
                    hardwareProfileName))

        sp = hp.mappedsoftwareprofiles[0]

    if sp and 'softwareProfile' not in addNodesRequest:
        addNodesRequest['softwareProfile'] = sp.name

    if 'hardwareProfile' not in addNodesRequest:
        addNodesRequest['hardwareProfile'] = hp.name

    # Validate 'nodeDetails'
    if nodeDetails:
        # Reconcile nodeDetails that contain hostnames with hwp name
        # format
        bWildcardNameFormat = hp.nameFormat == '*'
        hostname = nodeDetails[0]['name'] \
            if 'name' in nodeDetails[0] else None
        if (hostname and not bWildcardNameFormat and not
            addNodesRequest.get('skip_hostname_hwprofile_validation', False)):
            # Host name specified, but hardware profile does not
            # allow setting the host name
            raise InvalidArgument(
                'Hardware profile does not allow setting'
                ' host names of imported nodes')

        if nodeCount > 0 and nodeCount != len(nodeDetails):
            raise InvalidArgument(
                'Node count must be equal to number'
                ' of MAC/IP/node names provided')

    # check if software profile is locked
    if sp.lockedState:
        if sp.lockedState == 'HardLocked':
            raise OperationFailed(
                'Nodes cannot be added to hard locked software'
                ' profile [{}]'.format(sp.name))
        elif sp.lockedState == 'SoftLocked':
            if 'force' not in addNodesRequest or \
                    not addNodesRequest['force']:
                raise OperationFailed(
                    'Use --force argument to add nodes to soft locked'
                    f' software profile [{sp.name}]'
                )

    # ensure adding nodes does not exceed imposed limits
    node_count_validator.validate_add_count(session, sp.name, nodeCount)

    # Prohibit running add-host against installer
    validate_hwprofile(hp)

    # If the given hardwareProfile's nameFormat contains "#R',
    # then the rackNumber is required.
    nameFormat = hp.nameFormat

    if nameFormat.find('#R') != -1 and rackNumber is None:
        raise InvalidArgument(
            'Missing "rackNumber" for name format [%s] of'
            ' hardware profile [%s]' % (nameFormat, hp))

    adapter = resourceAdapterFactory.get_api(hp.resourceadapter.name)
    adapter.session = session

    adapter.validate_start_arguments(
        addNodesRequest, hp, dbSoftwareProfile=sp)


def decrypt_insertnode_request(key: bytes, token: str) -> Dict[str, Any]:
    """
    Raises Exception if the token can't be decrypted
    """
    f = Fernet(key)
    return json.loads(f.decrypt(token))


def encrypt_insertnode_request(key: bytes,  request: Dict[str, Any]) -> str:
    """
    Raises Exception if the token can't be decrypted
    """
    f = Fernet(key)
    return f.encrypt(json.dumps(request).encode())


def checkProfilesMapped(swProfile: SoftwareProfile, hwProfile: HardwareProfile):
    """
    Raises ProfileMappingNotAllowed if specified profiles are not
    mapped.
    """

    for mapped_hwprofile in swProfile.hardwareprofiles:
        if mapped_hwprofile.name == hwProfile.name:
            return

    raise ProfileMappingNotAllowed(
        'Software profile [%s] not mapped to hardware'
        ' profile [%s]' % (swProfile.name, hwProfile.name))


def validate_hwprofile(hp: HardwareProfile) -> None:
    """
    Raises InvalidArgument if specified hardware profile is that of the
    installer node
    """

    installer_fqdn = ConfigManager().getInstaller()

    for hwprofile_node in hp.nodes:
        if hwprofile_node.name == installer_fqdn:
            raise InvalidArgument(
                'Nodes cannot be added to Tortuga installer'
                ' hardware/software profiles')
