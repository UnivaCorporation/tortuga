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

# pylint: disable=no-member

from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.db.dbManager import DbManager
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.exceptions.nodeAlreadyExists import NodeAlreadyExists
from tortuga.db.nodes import Nodes
from tortuga.exceptions.profileMappingNotAllowed \
    import ProfileMappingNotAllowed
from tortuga.config.configManager import ConfigManager


def validate_addnodes_request(addNodesRequest):
    """
    Raises:
        HardwareProfileNotFound
        SoftwareProfileNotFound
        ProfileMappingNotAllowed
        InvalidArgument
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

    session = DbManager().openSession()

    try:
        # Look up hardware profile
        hp = hpapi.getHardwareProfile(session, hardwareProfileName) \
            if hardwareProfileName else None

        # Look up software profile
        sp = spapi.getSoftwareProfile(
            session, softwareProfileName) if softwareProfileName else None

        if sp and not sp.isIdle and 'isIdle' in addNodesRequest and \
                addNodesRequest['isIdle']:
            raise InvalidArgument(
                'Software profile [%s] is not idle software profile' % (
                    softwareProfileName))

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
        elif hp is not None and sp is None and not addNodesRequest['isIdle']:
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

        # Ensure user does not make a request for DHCP discovery mode.
        # Currently, this is determined by the presence of the item
        # 'nodeDetails' in addNodesRequest. Ultimately, this should be
        # shared code between here and the default resource adapter.
        if hp.resourceadapter and \
                hp.resourceadapter.name == 'default' and not nodeDetails:
            raise InvalidArgument(
                'DHCP discovery is not available through WS API.')

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
            if hostname and not bWildcardNameFormat:
                # Host name specified, but hardware profile does not
                # allow setting the host name
                raise InvalidArgument(
                    'Hardware profile does not allow setting'
                    ' host names of imported nodes')
            elif not hostname and bWildcardNameFormat:
                # Host name not specified but hardware profile expects it
                raise InvalidArgument(
                    'Hardware profile requires imported node'
                    ' name to be set')

            if nodeCount > 0 and nodeCount != len(nodeDetails):
                raise InvalidArgument(
                    'Node count must be equal to number'
                    ' of MAC/IP/node names provided')

            if hostname:
                # Ensure host does not already exist
                existing_node = session.query(Nodes).filter(
                    Nodes.name == hostname).first()
                if existing_node:
                    raise NodeAlreadyExists(
                        'Node [%s] already exists' % (hostname))

        # Prohibit running add-host against installer
        validate_hwprofile(hp)

        # If the given hardwareProfile's nameFormat contains "#R',
        # then the rackNumber is required.
        nameFormat = hp.nameFormat

        if nameFormat.find('#R') != -1 and rackNumber is None:
            raise InvalidArgument(
                'Missing "rackNumber" for name format [%s] of'
                ' hardware profile [%s]' % (nameFormat, hp))
        adapter = resourceAdapterFactory.getApi(hp.resourceadapter.name)

        adapter.validate_start_arguments(
            addNodesRequest, hp, dbSoftwareProfile=sp)
    finally:
        DbManager().closeSession()


def checkProfilesMapped(swProfile, hwProfile):
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


def validate_hwprofile(hp):
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
