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

import configparser
import os
from typing import Dict, List, Optional

from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.nodeAlreadyExists import NodeAlreadyExists
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.os_utility import osUtility, tortugaSubprocess
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter
from tortuga.resourceAdapter.utility import get_provisioning_nics
from tortuga.resourceAdapterConfiguration import settings as ra_settings


def initialize_nics(installer_provisioning_nic, hardwareprofilenetworks,
                    discovered_mac) -> List[dict]:
    # Return list of nic definitions based on hardware profile networks
    nics = []

    for hardwareprofilenetwork in hardwareprofilenetworks:
        nic = {}

        if hardwareprofilenetwork.networkId == \
                installer_provisioning_nic.network.id:
            # Set the discovered MAC on the provisioning interface
            nic['mac'] = discovered_mac

        nics.append(nic)

    return nics


class Default(ResourceAdapter):
    __adaptername__ = 'default'

    settings: Dict[str, ra_settings.BaseSetting] = {
        'boot_host_hook_script': ra_settings.FileSetting()
    }

    def __init__(self, addHostSession: Optional[str] = None) -> None:
        super().__init__(addHostSession=addHostSession)

        self._bhm = \
            osUtility.getOsObjectFactory().getOsBootHostManager(self._cm)

    @property
    def hookScript(self):
        '''
        Load the hook script setting from the resource adapter
        configuration file and ensure it exists. If the hook script is
        not defined or is defined and does note exist, a warning message
        is logged and the method returns None.
        '''

        RA_SECTION = 'resource-adapter'
        OPTION = 'host_hook_script'

        cfgFile = configparser.ConfigParser()
        cfgFile.read(self.cfgFileName)

        if not cfgFile.has_section(RA_SECTION) or \
                not cfgFile.has_option(RA_SECTION, OPTION):
            self._logger.warning('Hook script is not defined')

            return None

        hookScript = cfgFile.get(RA_SECTION, OPTION)

        if not hookScript[0] in ['/', '$']:
            tmpHookScript = os.path.join(
                self._cm.getKitConfigBase(), hookScript)
        else:
            tmpHookScript = hookScript.replace(
                '$TORTUGA_ROOT', self._cm.getRoot())

        if not os.path.join(tmpHookScript):
            self._logger.warning(
                'Hook script [%s] does not exist' % (tmpHookScript))

            return None

        return tmpHookScript

    def hookAction(self, action, nodes, args=None):
        '''
        WARNING: this method may be subject to scalability concerns if
        batch node operations are implemented.
        '''

        hookScript = self.hookScript

        if not hookScript:
            return

        nodeArg = nodes if not isinstance(nodes, list) else ','.join(nodes)

        cmd = '%s %s' % (hookScript, action)

        if args:
            cmd += ' %s' % (args)

        cmd += ' %s' % (nodeArg)

        tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def deleteNode(self, nodes: List[Node]) -> None:
        """Remove boot configuration for deleted nodes
        """
        for node in nodes:
            self.__delete_boot_configuration(node)

        self.hookAction('delete', [node.name for node in nodes])

    def __delete_boot_configuration(self, node: Node) -> None:
        """Remove PXE boot files and DHCP configuration
        """
        self._bhm.rmPXEFile(node)
        self._bhm.removeDhcpLease(node)

    def rebootNode(self, nodes: List[Node],
                   bSoftReset: Optional[bool] = False):
        self._logger.debug('rebootNode()')

        # Call the reboot script hook
        self.hookAction('reset', [node.name for node in nodes],
                        'soft' if bSoftReset else 'hard')

    def __get_node_details(self, addNodesRequest, dbHardwareProfile,
                           dbSoftwareProfile): \
            # pylint: disable=no-self-use,unused-argument
        nodeDetails = addNodesRequest['nodeDetails'] \
            if 'nodeDetails' in addNodesRequest else []

        # Check if any interface has predefined MAC address
        macSpecified = nodeDetails and \
            'nics' in nodeDetails[0] and \
            [nic_ for nic_ in nodeDetails[0]['nics'] if 'mac' in nic_]

        # Check if any intercace has predefined IP address
        ipAddrSpecified = nodeDetails and \
            'nics' in nodeDetails[0] and \
            [ip_ for ip_ in nodeDetails[0]['nics'] if 'ip' in ip_]

        hostNameSpecified = nodeDetails and 'name' in nodeDetails[0]

        if macSpecified or ipAddrSpecified or hostNameSpecified:
            return nodeDetails

        return None

    def start(self, addNodesRequest, dbSession, dbHardwareProfile,
              dbSoftwareProfile=None) -> List[Node]:
        """
        Raises:
            CommandFailed
        """

        # 'nodeDetails' is a list of details (contained in a 'dict') for
        # one or more nodes. It can contain host name(s) and nic details
        # like MAC and/or IP address. It is an entirely optional data
        # structure and may be empty and/or undefined.

        nodeDetails = self.__get_node_details(
            addNodesRequest, dbHardwareProfile, dbSoftwareProfile)

        if not nodeDetails:
            raise CommandFailed('Invalid operation (DHCP discovery)')

        try:
            dns_zone = GlobalParametersDbHandler().getParameter(
                dbSession, 'DNSZone').value
        except ParameterNotFound:
            dns_zone = ''

        nodes = self.__add_predefined_nodes(
            addNodesRequest, dbSession, dbHardwareProfile, dbSoftwareProfile,
            dns_zone=dns_zone)

        # This is a necessary evil for the time being, until there's
        # a proper context manager implemented.
        self.addHostApi.clear_session_nodes(nodes)

        return nodes

    def validate_start_arguments(self, addNodesRequest: dict,
                                 dbHardwareProfile: HardwareProfile,
                                 dbSoftwareProfile: SoftwareProfile): \
            # pylint: disable=unused-argument,no-self-use
        '''
        :raises CommandFailed:
        :raises NodeAlreadyExists:
        '''

        if dbSoftwareProfile is None:
            raise CommandFailed(
                "Software profile must be provided when adding nodes"
                " to this hardware profile")

        if dbHardwareProfile.location != 'local':
            # Only ensure that required installer components are enabled when
            # hardware profile is marked as 'local'.
            return

        # All resource adapters are responsible for doing their own
        # check for the configuration.  This may change in the
        # future!

        dbInstallerNode = dbHardwareProfile.nics[0].node \
            if dbHardwareProfile.nics else \
            NodesDbHandler().getNode(self.session, self._cm.getInstaller())

        components = [c for c in dbInstallerNode.softwareprofile.components
                      if c.name == 'dhcpd']

        if not components:
            raise CommandFailed(
                'dhcpd component must be enabled on the'
                ' installer in order to provision local nodes')

        name_expected = dbHardwareProfile.nameFormat == '*'

        nodeDetails = addNodesRequest['nodeDetails'] \
            if 'nodeDetails' in addNodesRequest and \
            addNodesRequest['nodeDetails'] else None

        # extract host name from addNodesRequest
        name = nodeDetails[0]['name'] \
            if nodeDetails and 'name' in nodeDetails[0] else None

        mac_addr = None

        if nodeDetails and 'nics' in nodeDetails[0]:
            for nic in nodeDetails[0]['nics']:
                if 'mac' in nic:
                    mac_addr = nic['mac']
                    break

        # check if name is expected in nodeDetails
        if not nodeDetails and name_expected and not name:
            raise CommandFailed(
                'Name and MAC address must be specified for nodes'
                ' in hardware profile [%s]' % dbHardwareProfile.name
            )

        if not nodeDetails and not mac_addr:
            raise CommandFailed(
                'MAC address must be specified for nodes in'
                ' hardware profile [%s]' % dbHardwareProfile.name
            )

        # if host name specified, ensure host does not already exist
        if name:
            try:
                NodesDbHandler().getNode(self.session, name)

                raise NodeAlreadyExists('Node [%s] already exists' % name)
            except NodeNotFound:
                # node does not already exist
                pass

    def __add_predefined_nodes(self, addNodesRequest: dict, dbSession,
                               dbHardwareProfile, dbSoftwareProfile,
                               dns_zone: str = None) -> List[Node]:
        nodeDetails = addNodesRequest['nodeDetails'] \
            if 'nodeDetails' in addNodesRequest else []

        bGenerateIp = dbHardwareProfile.location != 'remote'

        newNodes = []

        for nodeDict in nodeDetails:
            addNodeRequest = {}

            addNodeRequest['addHostSession'] = self.addHostSession

            if 'rack' in addNodesRequest:
                # rack can be undefined, in which case it is not copied
                # into the node request
                addNodeRequest['rack'] = addNodesRequest['rack']

            if 'nics' in nodeDict:
                addNodeRequest['nics'] = nodeDict['nics']

            if 'name' in nodeDict:
                addNodeRequest['name'] = nodeDict['name']

            node = self.nodeApi.createNewNode(
                dbSession, addNodeRequest, dbHardwareProfile,
                dbSoftwareProfile, bGenerateIp=bGenerateIp, dns_zone=dns_zone)

            dbSession.add(node)

            # Create DHCP/PXE configuration
            self.writeLocalBootConfiguration(
                node, dbHardwareProfile, dbSoftwareProfile)

            # Get the provisioning nic
            nics = get_provisioning_nics(node)

            self._pre_add_host(
                node.name,
                dbHardwareProfile.name,
                dbSoftwareProfile.name,
                nics[0].ip if nics else None)

            newNodes.append(node)

        return newNodes

    def stop(self, hardwareProfileName, deviceName): \
            # pylint: disable=unused-argument
        pass

    def addVolumeToNode(self, node, volume, isDirect=True):
        '''Add a disk to a node'''
        if not isDirect:
            raise UnsupportedOperation(
                'This node only supports direct volume attachment.')

        # Map the volume to a driveNumber
        openDriveNumber = self.sanApi.mapDrive(node, volume)

        try:
            # have the node connect the storage
            self.sanApi.connectStorageVolume(node, volume, node.getName())
        except Exception:  # noqa pylint: disable=broad-except
            self._logger.exception('Error adding volume to node')

            # Need to clean up mapping
            self.sanApi.unmapDrive(node, driveNumber=openDriveNumber)

            raise

    def removeVolumeFromNode(self, node, volume):
        '''Remove a disk from a node'''

        try:
            try:
                self.sanApi.disconnectStorageVolume(
                    node, volume, node.getName())
            except Exception:  # noqa pylint: disable=broad-except
                # Failed disconnect...
                self._logger.exception(
                    'Error disconnecting volume from node')

                raise
        finally:
            # Unmap Map the volume to a driveNumber
            self.sanApi.unmapDrive(node, volume=volume)

    def shutdownNode(self, nodes: List[Node],
                     bSoftReset: Optional[bool] = False):
        """
        Shutdown specified node(s)
        """

        self.hookAction(
            'shutdown', [node.name for node in nodes],
            'soft' if bSoftReset else 'hard')

    def startupNode(self, nodes: List[Node],
                    remainingNodeList: Optional[str] = None,
                    tmpBootMethod: Optional[str] = 'n'): \
            # pylint: disable=unused-argument
        """
        Start the given node(s)
        """

        self.hookAction('start', [node.name for node in nodes])
