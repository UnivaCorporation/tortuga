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
import select
import signal
from typing import Dict, List

from tortuga.db.dbManager import DbManager
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.nodes import Nodes
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.ipAlreadyExists import IpAlreadyExists
from tortuga.exceptions.macAddressAlreadyExists \
    import MacAddressAlreadyExists
from tortuga.exceptions.nodeAlreadyExists import NodeAlreadyExists
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.os_utility import osUtility
from tortuga.os_utility import tortugaSubprocess
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter
from tortuga.resourceAdapter.utility import get_provisioning_nic, \
    get_provisioning_nics
from tortuga.objects import resourceadapter_settings


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

    settings: Dict[str, resourceadapter_settings.BaseSetting] = {
        'boot_host_hook_script': resourceadapter_settings.FileSetting()
    }

    def __init__(self, addHostSession=None):
        super(Default, self).__init__(addHostSession=addHostSession)

        self.looping = False

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
            self.getLogger().warning('Hook script is not defined')

            return None

        hookScript = cfgFile.get(RA_SECTION, OPTION)

        if not hookScript[0] in ['/', '$']:
            tmpHookScript = os.path.join(
                self._cm.getKitConfigBase(), hookScript)
        else:
            tmpHookScript = hookScript.replace(
                '$TORTUGA_ROOT', self._cm.getRoot())

        if not os.path.join(tmpHookScript):
            self.getLogger().warning(
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

    def transferNode(self, nodeIdSoftwareProfileTuples,
                     newSoftwareProfileName): \
            # pylint: disable=unused-argument
        """
        Raises:
            NodeNotFound
        """

        bhm = osUtility.getOsObjectFactory().getOsBootHostManager()

        for dbNode, _ in nodeIdSoftwareProfileTuples:
            # Ensure PXE files are properly in place before triggering
            # the reboot.
            bhm.setNodeForNetworkBoot(dbNode)

        self.rebootNode([dbNode for dbNode, _ in nodeIdSoftwareProfileTuples])

    def suspendActiveNode(self, nodeId): \
            # pylint: disable=no-self-use,unused-argument
        return False

    def idleActiveNode(self, dbNodes):
        # Shutdown nodes
        self.shutdownNode(dbNodes)

        return 'Discovered'

    def activateIdleNode(self, dbNode, softwareProfileName,
                         softwareProfileChanged): \
            # pylint: disable=no-self-use
        bhm = osUtility.getOsObjectFactory().getOsBootHostManager()

        session = DbManager().openSession()

        try:
            if softwareProfileChanged:
                softwareprofile = SoftwareProfilesDbHandler().\
                    getSoftwareProfile(session, softwareProfileName)

                # Mark node for network boot if software profile changed
                dbNode.bootFrom = 0
            else:
                softwareprofile = None

            bhm.writePXEFile(dbNode,
                             localboot=not softwareProfileChanged,
                             softwareprofile=softwareprofile)
        finally:
            DbManager().closeSession()

    def abort(self):
        self.looping = False

    def deleteNode(self, dbNodes):
        self.hookAction('delete', [dbNode.name for dbNode in dbNodes])

    def rebootNode(self, dbNodes, bSoftReset=False):
        self.getLogger().debug('rebootNode()')

        # Call the reboot script hook
        self.hookAction('reset', [dbNode.name for dbNode in dbNodes],
                        'soft' if bSoftReset else 'hard')

    def __is_duplicate_mac_in_session(self, mac, session_nodes): \
            # pylint: disable=no-self-use
        for node in session_nodes:
            for nic in node.nics:
                if nic.mac == mac:
                    return True

        return False

    def __is_duplicate_mac(self, mac, session_nodes):
        if self.__is_duplicate_mac_in_session(mac, session_nodes):
            return True

        session = DbManager().openSession()

        try:
            NodesDbHandler().getNodeByMac(session, mac)

            return True
        except NodeNotFound:
            return False

        finally:
            DbManager().closeSession()

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
              dbSoftwareProfile=None) -> List[Nodes]:
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

        # return self.__add_predefined_nodes(
        #     addNodesRequest, dbSession, dbHardwareProfile,
        #     dbSoftwareProfile) \
        #     if nodeDetails else self.__dhcp_discovery(
        #         addNodesRequest, dbSession, dbHardwareProfile,
        #         dbSoftwareProfile)

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

    def validate_start_arguments(self, addNodesRequest, dbHardwareProfile,
                                 dbSoftwareProfile): \
            # pylint: disable=unused-argument,no-self-use
        '''
        Raises:
            CommandFailed
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

        dbSession = DbManager().openSession()

        try:
            dbInstallerNode = dbHardwareProfile.nics[0].node \
                if dbHardwareProfile.nics else \
                NodesDbHandler().getNode(dbSession, self._cm.getInstaller())

            components = [c for c in dbInstallerNode.softwareprofile.components
                          if c.name == 'dhcpd']

            if not components:
                raise CommandFailed(
                    'dhcpd component must be enabled on the'
                    ' installer in order to provision local nodes')
        finally:
            DbManager().closeSession()

    def __add_predefined_nodes(self, addNodesRequest: dict, dbSession,
                               dbHardwareProfile, dbSoftwareProfile,
                               dns_zone: str = None) -> List[Nodes]:
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

    def __dhcp_discovery(self, addNodesRequest, dbSession, dbHardwareProfile,
                         dbSoftwareProfile):
        # Listen for DHCP requests

        if not dbHardwareProfile.nics:
            raise CommandFailed(
                'Hardware profile [%s] does not have a provisioning'
                ' NIC defined' % (dbHardwareProfile.name))

        newNodes = []

        deviceName = addNodesRequest['deviceName'] \
            if 'deviceName' in addNodesRequest else None

        nodeCount = addNodesRequest['count'] \
            if 'count' in addNodesRequest else 0

        bGenerateIp = dbHardwareProfile.location != 'remote'

        # Obtain platform-specific packet capture subprocess object
        addHostManager = osUtility.getOsObjectFactory().getOsAddHostManager()

        deviceName = dbHardwareProfile.nics[0].networkdevice.name

        p1 = addHostManager.dhcpCaptureSubprocess(deviceName)

        if nodeCount:
            self.getLogger().debug(
                'Adding [%s] new %s' % (
                    nodeCount, 'nodes' if nodeCount > 1 else 'node'))

        self.looping = True

        index = 0

        # Node count was not specified, so discover DHCP nodes
        # until manually aborted by user.
        msg = 'Waiting for new node...' if not nodeCount else \
            'Waiting for new node #1 of %d...' % (nodeCount)

        try:
            while self.looping:
                # May not need this...
                dataReady = select.select([p1.stdout], [], [], 5)

                if not dataReady[0]:
                    continue

                line = p1.stdout.readline()

                if not line:
                    self.getLogger().debug(
                        'DHCP packet capture process ended... exiting')

                    break

                self.getLogger().debug(
                    'Read line "%s" len=%s' % (line, len(line)))

                mac = addHostManager.getMacAddressFromCaptureEntry(line)

                if not mac:
                    continue

                self.getLogger().debug('Discovered MAC address [%s]' % (mac))

                if self.__is_duplicate_mac(mac, newNodes):
                    # Ignore DHCP request from known MAC
                    self.getLogger().debug(
                        'MAC address [%s] is already known' % (mac))

                    continue

                addNodeRequest = {}

                if 'rack' in addNodesRequest:
                    addNodeRequest['rack'] = addNodesRequest['rack']

                # Get nics based on hardware profile networks
                addNodeRequest['nics'] = initialize_nics(
                    dbHardwareProfile.nics[0],
                    dbHardwareProfile.hardwareprofilenetworks, mac)

                # We may be trying to create the same node for the
                # second time so we'll ignore errors
                try:
                    node = self.nodeApi.createNewNode(
                        None,
                        addNodeRequest,
                        dbHardwareProfile,
                        dbSoftwareProfile,
                        bGenerateIp=bGenerateIp)
                except NodeAlreadyExists as ex:
                    existingNodeName = ex.args[0]

                    self.getLogger().debug(
                        'Node [%s] already exists' % (existingNodeName))

                    continue
                except MacAddressAlreadyExists:
                    self.getLogger().debug(
                        'MAC address [%s] already exists' % (mac))

                    continue
                except IpAlreadyExists as ex:
                    self.getLogger().debug(
                        'IP address already in use by node'
                        ' [%s]: %s' % (existingNodeName, ex))

                    continue

                # Add the newly created node to the session
                dbSession.add(node)

                # Create DHCP/PXE configuration
                self.writeLocalBootConfiguration(
                    node, dbHardwareProfile, dbSoftwareProfile)

                index += 1

                # Use first provisioning nic
                nic = get_provisioning_nic(node)

                try:
                    msg = 'Added node [%s] IP [%s]' % (
                        node.name, nic.ip)

                    if nic.mac:
                        msg += ' MAC [%s]' % (nic.mac)

                    self.getLogger().info(msg)
                except Exception as ex:
                    self.getLogger().exception('Error setting status message')

                self._pre_add_host(
                    node.name,
                    dbHardwareProfile.name,
                    dbSoftwareProfile.name,
                    nic.ip)

                newNodes.append(node)

                if nodeCount > 0:
                    nodeCount -= 1
                    if not nodeCount:
                        self.looping = False
        except Exception as msg:
            self.getLogger().exception('DHCP discovery failed')

        try:
            os.kill(p1.pid, signal.SIGKILL)
            os.waitpid(p1.pid, 0)
        except Exception:
            self.getLogger().exception(
                'Error killing network capture process')

        # This is a necessary evil for the time being, until there's
        # a proper context manager implemented.
        self.addHostApi.clear_session_nodes(newNodes)

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
        except Exception:
            self.getLogger().exception('Error adding volume to node')

            # Need to clean up mapping
            self.sanApi.unmapDrive(node, driveNumber=openDriveNumber)

            raise

    def removeVolumeFromNode(self, node, volume):
        '''Remove a disk from a node'''

        try:
            try:
                self.sanApi.disconnectStorageVolume(
                    node, volume, node.getName())
            except Exception:
                # Failed disconnect...
                self.getLogger().exception(
                    'Error disconnecting volume from node')

                raise
        finally:
            # Unmap Map the volume to a driveNumber
            self.sanApi.unmapDrive(node, volume=volume)

    def shutdownNode(self, dbNodes, bSoftShutdown=False):
        '''Shutdown specified node(s)'''

        self.hookAction(
            'shutdown', [dbNode.name for dbNode in dbNodes],
            'soft' if bSoftShutdown else 'hard')

    def startupNode(self, dbNodes, remainingNodeList=None,
                    tmpBootMethod='n'): \
            # pylint: disable=unused-argument
        '''Start the given node(s)'''

        self.hookAction('start', [dbNode.name for dbNode in dbNodes])
