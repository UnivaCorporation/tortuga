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

# pylint: disable=logging-not-lazy,no-self-use,no-member,maybe-no-member

import csv
import logging
import os.path
import socket
import subprocess
import sys
import traceback
from typing import Any, Dict, List, NoReturn, Optional, Union

import gevent
from sqlalchemy.orm.session import Session

from tortuga.addhost.addHostManager import AddHostManager
from tortuga.config.configManager import ConfigManager
from tortuga.db.dbManager import DbManager
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.network import Network
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.resourceAdapterConfig import ResourceAdapterConfig
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.resourceAdapterConfigDbHandler import \
    ResourceAdapterConfigDbHandler
from tortuga.events.types.node import NodeStateChanged
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.resourceNotFound import ResourceNotFound
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.objects.node import Node as TortugaNode
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.parameter.parameterApi import ParameterApi
from tortuga.schema import ResourceAdapterConfigSchema

from .userDataMixin import UserDataMixin


class ResourceAdapter(UserDataMixin): \
        # pylint: disable=too-many-public-methods
    """
    This is the base class for all resource adapters to derive from.
    The default actions simply print a debug message to show that the
    subclass did not implement the action.

    """
    settings = {}

    __adaptername__ = None

    def __init__(self, addHostSession: Optional[str] = None):
        if not self.__adaptername__:
            raise AttributeError(
                'Subclasses of ResourceAdapter must have __adaptername__'
                ' defined')

        self._logger = logging.getLogger(
            'tortuga.resourceAdapter.%s' % (self.__adaptername__))
        self._logger.addHandler(logging.NullHandler())

        self.__installer_public_hostname = None
        self.__installer_public_ipaddress = None
        self.__private_dns_zone = None

        # Initialize caches
        self.__addHostApi = None
        self.__nodeApi = None
        self.__osObject = None
        self.__sanApi = None

        self._cm = ConfigManager()

        self._addHostSession = addHostSession

    @property
    def addHostSession(self):
        return self._addHostSession

    @property
    def cacheCfgFilePath(self):
        return os.path.join(
            self._cm.getRoot(), 'var', '%s-instance.conf' % (
                self.__adaptername__))

    @property
    def cfgFileName(self):
        return os.path.join(
            self._cm.getKitConfigBase(),
            'adapter-defaults-%s.conf' % (
                self.__adaptername__))

    def hookAction(self, action, nodes, args=None):
        # Only the 'default' resource adapter overrides the hookAction()
        # method.
        pass

    def start(self, addNodesRequest: dict, dbSession: Session,
              dbHardwareProfile: HardwareProfile,
              dbSoftwareProfile: Optional[SoftwareProfile] = None): \
            # pylint: disable=unused-argument
        self.__trace(
            addNodesRequest, dbSession, dbHardwareProfile,
            dbSoftwareProfile)

    def fire_state_change_event(self, db_node: Node, previous_state: str):
        """
        Fires a node state changed event. This is a "fake" operation allowing
        resource adapters to fire events without having to actually take
        the node through the actual state change. The node is assumed to
        have it's current state set to the new state.

        :param Node db_node:       a database node instance
        :param str previous_state: the previous state for the node

        """
        node_dict = TortugaNode.getFromDbDict(db_node.__dict__).getCleanDict()
        NodeStateChanged.fire(node=node_dict,
                              previous_state=previous_state)

    def fire_provisioned_event(self, db_node: Node):
        """
        Fires the node provisioned event. This is a fake operation that
        assumes two things: that the node's current state is already set
        as "Provisioned" and that the previous state was "Created". If you
        need it to behave differently from that, then you need to sue the
        "fire_state_change_event" method instead.

        :param Node db_node: the database node instance

        """
        self.fire_state_change_event(db_node=db_node,
                                     previous_state='Created')

    def validate_start_arguments(self, addNodesRequest: dict,
                                 dbHardwareProfile: HardwareProfile,
                                 dbSoftwareProfile: SoftwareProfile):
        self.__trace(
            addNodesRequest, dbHardwareProfile, dbSoftwareProfile)

    def stop(self, hardwareProfileName: str, deviceName: str):
        self.__trace(hardwareProfileName, deviceName)

    def updateNode(self, session: Session, node: Node,
                   updateNodeRequest: dict): \
            # pylint: disable=unused-argument
        self.__trace(session, node, updateNodeRequest)

    def suspendActiveNode(self, node: Node) -> bool:
        """
        Change the given active node to an idle node
        """

        self.__trace(node)

    def idleActiveNode(self, nodes: List[Node]) -> str:
        """
        Change the given active node to an idle node
        """

        self.__trace(nodes)

    def activateIdleNode(self, node: Node, softwareProfileName: str,
                         softwareProfileChanged: bool):
        """
        Change the given idle node to an active node
        """

        self.__trace(node, softwareProfileName, softwareProfileChanged)

    def deleteNode(self, nodes: List[Node]) -> NoReturn:
        """
        Remove the given node (active or idle) from the system
        """

        self.__trace(nodes)

    def _async_delete_nodes(self, nodes):
        """
        Asynchronously delete nodes; calls "ResourceAdapter._delete_node()"
        method for each deleted nodes

        :param dbNodes: list of Nodes objects
        :return: None
        """
        greenlets = []

        for node in nodes:
            greenlets.append(gevent.spawn(self._delete_node, node))

        # TODO: implement timeout
        gevent.joinall(greenlets)

    def transferNode(self, nodeIdSoftwareProfileTuples,
                     newSoftwareProfileName: str):
        """Transfer the given idle node"""
        self.__trace(nodeIdSoftwareProfileTuples, newSoftwareProfileName)

    def startupNode(self, nodes: List[Node],
                    remainingNodeList: Optional[str] = None,
                    tmpBootMethod: Optional[str] = 'n'): \
            # pylint: disable=unused-argument
        """
        Start nodes
        """

        # By default raise unsupported operation
        raise UnsupportedOperation('Node does not support starting')

    def shutdownNode(self, nodes: List[Node],
                     bSoftReset: Optional[bool] = False): \
            # pylint: disable=unused-argument
        """Shutdown the given node"""
        # By default raise unsupported operation
        raise UnsupportedOperation('Node does not support shutdown')

    def rebootNode(self, nodes: List[Node],
                   bSoftReset: Optional[bool] = False): \
            # pylint: disable=unused-argument
        """Reboot the given node"""
        # By default raise unsupported operation
        raise UnsupportedOperation('Node does not support rebooting')

    def addVolumeToNode(self, node: Node, volume: str, isDirect: bool): \
            # pylint: disable=unused-argument
        """Add a disk to a node"""
        # By default raise unsupported operation
        raise UnsupportedOperation(
            'Node does not support dynamic disk addition')

    def removeVolumeFromNode(self, node: Node, volume: str): \
            # pylint: disable=unused-argument
        """Remove a disk from a node"""
        # By default raise unsupported operation
        raise UnsupportedOperation(
            'Node does not support dynamic disk deletion' % (node))

    def __trace(self, *pargs, **kargs) -> NoReturn:
        stack = traceback.extract_stack()
        funcname = stack[-2][2]

        self._logger.debug(
            '-- (pass) %s::%s %s %s' % (
                self.__adaptername__, funcname, pargs, kargs))

    def getLogger(self):
        return self._logger

    def getResourceAdapterConfig(self,
                                 sectionName: Union[str, None] = None) -> dict:
        """
        Raises:
            ResourceNotFound
        """

        self.getLogger().debug(
            'getResourceAdapterConfig(sectionName=[{0}])'.format(
                sectionName if sectionName else '(none)'))

        try:
            # Load default values
            defaultResourceAdapterConfigDict = self._loadConfigDict()

            if sectionName is None or sectionName == 'default':
                return defaultResourceAdapterConfigDict
        except ResourceNotFound:
            defaultResourceAdapterConfigDict = {}

        overrideConfigDict = self._loadConfigDict(sectionName)

        # Override defaults with hardware profile specific settings
        return dict(
            list(defaultResourceAdapterConfigDict.items()) +
            list(overrideConfigDict.items()))

    def _normalize_resource_adapter_config(
            self, configDict: Dict[str, Any]) -> Dict[str, Any]:
        # no-op by default
        return configDict

    def _loadConfigDict(self, sectionName: Union[str, None] = None) \
            -> Dict[str, str]:
        """
        Retrieve resource adapter configuration from database.

        Raises:
            ResourceNotFound
        """

        self.getLogger().debug(
            '_loadConfigDict(): sectionName=[{}]'.format(
                sectionName if sectionName else 'default'))

        with DbManager().session() as session:
            cfg = ResourceAdapterConfigSchema().dump(
                self.load_resource_adapter_config(session, sectionName)
            ).data

            return {s['key']: s['value'] for s in cfg['settings']}

    def __getAddHostApi(self):
        """Get and cache the Add Host API"""

        if self.__addHostApi is None:
            from tortuga.addhost.addHostServerLocal \
                import AddHostServerLocal

            self.__addHostApi = AddHostServerLocal()

        return self.__addHostApi

    def __getNodeApi(self):
        """Get and cache the Node API"""

        if self.__nodeApi is None:
            from tortuga.node.nodeApi import NodeApi
            self.__nodeApi = NodeApi()
        return self.__nodeApi

    def __getOsObject(self):
        """Get and cache the OS Object Factory"""

        if self.__osObject is None:
            from tortuga.os_utility import osUtility
            self.__osObject = osUtility.getOsObjectFactory()
        return self.__osObject

    def __getSanApi(self):
        """Internal: Get and cache the SAN API"""

        if self.__sanApi is None:
            from tortuga.san import san
            self.__sanApi = san.San()
        return self.__sanApi

    # Properties for this object
    addHostApi = property(__getAddHostApi, None, None, None)
    nodeApi = property(__getNodeApi, None, None, None)
    osObject = property(__getOsObject, None, None, None)
    sanApi = property(__getSanApi, None, None, None)

    def statusMessage(self, msg: str) -> NoReturn:
        if self._addHostSession:
            AddHostManager().updateStatus(
                self._addHostSession, msg)
        else:
            # Just print out the message...this is a stop gap for resource
            # adapters running outside of the addHostManager framework
            sys.stdout.write(msg + '\n')
            sys.stdout.flush()

    def getOptions(self, dbSoftwareProfile: SoftwareProfile,
                   dbHardwareProfile: HardwareProfile) -> dict: \
            # pylint: disable=unused-argument
        return {}

    def __findNicForProvisioningNetwork(self, nics: List[Nic],
                                        prov_network: Network) -> Nic:
        """
        TODO: move this elsewhere

        Raises:
            NicNotFound
        """

        nics = [nic for nic in nics if nic.network == prov_network]

        if not nics:
            raise NicNotFound(
                'Unable to find NIC on provisioning network [%s]' % (
                    prov_network.address + '/' + prov_network.netmask))

        return nics[0]

    def writeLocalBootConfiguration(self, node: Node,
                                    hardwareprofile: HardwareProfile,
                                    softwareprofile: SoftwareProfile):
        """
        Raises:
            NicNotFound
        """

        if not hardwareprofile.nics:
            # Hardware profile has no provisioning NICs defined. This
            # shouldn't happen...

            self.getLogger().debug(
                'No provisioning nics defined in hardware profile %s' % (
                    hardwareprofile.name))

            return

        # Determine the provisioning nic for the hardware profile
        hwProfileProvisioningNic = hardwareprofile.nics[0]

        nic = None

        if hwProfileProvisioningNic.network:
            # Find the nic attached to the newly added node that is on
            # the same network as the provisioning nic.
            nic = self.__findNicForProvisioningNetwork(
                node.nics, hwProfileProvisioningNic.network)

        if not nic or not nic.mac:
            self.getLogger().warning(
                'MAC address not defined for nic (ip=[%s]) on node [%s]' % (
                    nic.ip, node.name))

            return

        # Set up DHCP/PXE for newly addded node
        bhm = getOsObjectFactory().getOsBootHostManager()

        # Write out the PXE file
        bhm.writePXEFile(
            node, hardwareprofile=hardwareprofile,
            softwareprofile=softwareprofile, localboot=False)

        # Add a DHCP lease
        bhm.addDhcpLease(node, nic)

    def removeLocalBootConfiguration(self, node: Node) -> NoReturn:
        bhm = self.osObject.getOsBootHostManager()

        bhm.rmPXEFile(node)
        bhm.removeDhcpLease(node)

    def _pre_add_host(self, name: str, hwprofilename: str, swprofilename: str,
                      ip: str) -> NoReturn: \
            # pylint: disable=unused-argument
        # Perform "pre-add-host" operation
        command = ('sudo %s/pre-add-host'
                   ' --hardware-profile %s'
                   ' --software-profile %s'
                   ' --host-name %s' % (
                       self._cm.getBinDir(),
                       hwprofilename,
                       swprofilename,
                       name))

        if ip:
            command += ' --ip %s' % (ip)

        self.getLogger().debug('calling command= [%s]' % (command))

        p = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True)

        p.communicate()

        p.wait()

    @property
    def installer_public_hostname(self) -> str:
        if self.__installer_public_hostname is None:

            cmd = '/opt/puppetlabs/bin/facter fqdn'

            with open(os.devnull, 'w') as devnull:
                p = subprocess.Popen(cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=devnull)

                stdout, _ = p.communicate()

                retval = p.wait()

            if retval == 0:
                self.__installer_public_hostname = stdout.decode().rstrip()

                self.getLogger().debug(
                    'using installerName [%s] from Facter' % (
                        self.__installer_public_hostname))
            else:
                self.__installer_public_hostname = self._cm.getHost()

                self.getLogger().debug(
                    'using installerName [%s] from system' % (
                        self.__installer_public_hostname))

        return self.__installer_public_hostname

    @property
    def installer_public_ipaddress(self) -> str:
        # Get installer IP
        if self.__installer_public_ipaddress is None:
            self.getLogger().debug('Looking up installer IP using DNS')

            aiInfo = socket.getaddrinfo(
                self.installer_public_hostname, None, socket.AF_INET,
                socket.SOCK_STREAM)

            self.__installer_public_ipaddress = aiInfo[0][4][0]

        return self.__installer_public_ipaddress

    @property
    def private_dns_zone(self) -> str:
        if self.__private_dns_zone is None:
            self.__private_dns_zone = \
                ParameterApi().getParameter('DNSZone').getValue()

        return self.__private_dns_zone

    def _get_config_file_path(self, filepath):
        """
        Raises:
            ConfigurationError
        """

        if filepath.startswith('/'):
            fn = filepath
        else:
            fn = os.path.join(self._cm.getKitConfigBase(), filepath)

        if not os.path.exists(fn):
            raise ConfigurationError(
                'Configuration file [{0}] does not exist'.format(fn))

        return fn

    def get_node_vcpus(self, name: str) -> int: \
            # pylint: disable=unused-argument
        return 1

    def get_instance_size_mapping(self, value) -> int:
        """
        Helper method for matching the first field (instance size) in
        the resource adapter specific CSV file

        :return: instance type/size to vcpus mapping
        :returntype int:
        """

        fn = os.path.join(
            self._cm.getKitConfigBase(),
            '{0}-instance-sizes.csv'.format(self.__adaptername__))

        if not os.path.exists(fn):
            return 1

        try:
            with open(fn) as fp:
                reader = csv.reader(fp)
                for row in reader:
                    if row[0] == value:
                        return int(row[1])

            return 1
        except Exception as exc:  # pylint: disable=broad-except
            self.getLogger().error(
                'Error processing instance type mapping'
                ' [{0}] (exc=[{1}]). Using default value'.format(fn, exc))

            return 1

    def get_node_resource_adapter_config(self, node: Node) \
            -> Dict[str, Any]:
        """
        Deserialize resource adapter configuration to key/value pairs
        """

        default_config = self._loadConfigDict()

        if node.instance and node.instance.resource_adapter_configuration:
            # break db relationship into key-value pairs for dict
            override_config = {
                c.key: c.value
                for c in
                node.instance.resource_adapter_configuration.settings
            }

            # override any settings in the configuration profile
            default_config.update(override_config)

        return self._normalize_resource_adapter_config(default_config)

    def load_resource_adapter_config(self, session: Session, name: str) \
            -> ResourceAdapterConfig:
        """
        Helper method to get resource adapter configuration

        Raises:
            ResourceNotFound
        """

        return ResourceAdapterConfigDbHandler().get(
            session,
            self.__adaptername__,
            name if name else 'default',
        )
