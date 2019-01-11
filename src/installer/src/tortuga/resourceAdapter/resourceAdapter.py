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
import sys
import traceback
from typing import Any, Dict, List, Optional

from sqlalchemy.orm.session import Session

import gevent
from tortuga.addhost.addHostManager import AddHostManager
from tortuga.config.configManager import ConfigManager
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
from tortuga.kit.actions.manager import KitActionsManager
from tortuga.objects.node import Node as TortugaNode
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.parameter.parameterApi import ParameterApi
from tortuga.resourceAdapterConfiguration.settings import BaseSetting
from tortuga.resourceAdapterConfiguration.validator import (ConfigurationValidator,
                                                            ValidationError)
from tortuga.schema import ResourceAdapterConfigSchema

from .userDataMixin import UserDataMixin


cm = ConfigManager()

DEFAULT_CONFIGURATION_PROFILE_NAME = 'Default'


class ResourceAdapter(UserDataMixin): \
        # pylint: disable=too-many-public-methods
    """
    This is the base class for all resource adapters to derive from.
    The default actions simply print a debug message to show that the
    subclass did not implement the action.

    """
    settings: Dict[str, BaseSetting] = {}

    __adaptername__ = None

    def __init__(self, addHostSession: Optional[str] = None):
        if not self.__adaptername__:
            raise AttributeError(
                'Subclasses of ResourceAdapter must have __adaptername__'
                ' defined')

        self._logger = logging.getLogger(
            'tortuga.resourceAdapter.%s' % (self.__adaptername__))

        self.__installer_public_hostname = None
        self.__installer_public_ipaddress = None
        self.__private_dns_zone = None

        # Initialize caches
        self.__addHostApi = None
        self.__nodeApi = None
        self.__osObject = None
        self.__sanApi = None

        self._cm = cm

        self._addHostSession = addHostSession

        self.session = None

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
                                 dbSoftwareProfile: SoftwareProfile): \
            # pylint: disable=unused-argument
        """
        Validate arguments (eventually) passed to start() API
        """

        cfgname = addNodesRequest.get('resource_adapter_configuration')
        if cfgname is None:
            # use default resource adapter configuration, if set
            cfgname = dbHardwareProfile.default_resource_adapter_config.name \
                if dbHardwareProfile.default_resource_adapter_config else \
                'Default'

        # ensure addNodesRequest reflects resource adapter configuration
        # profile being used
        addNodesRequest['resource_adapter_configuration'] = cfgname

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

    def deleteNode(self, nodes: List[Node]) -> None:
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

    def __trace(self, *pargs, **kargs) -> None:
        stack = traceback.extract_stack()
        funcname = stack[-2][2]

        self._logger.debug(
            '-- (pass) %s::%s %s %s' % (
                self.__adaptername__, funcname, pargs, kargs))

    def getLogger(self):
        return self._logger

    def validate_config(self, profile: str = 'Default') -> ConfigurationValidator:
        """
        Validates the configuration profile.

        :param str profile: the name of the configuration profile to validate

        :return ConfigurationValidator: the validator, loaded with the
                                        validated data

        :raises ValidationError:

        """
        validator = ConfigurationValidator(self.settings)

        #
        # Load settings from class settings definitions if any of them
        # have default values
        #
        validator.load(self._load_config_from_class())

        #
        # Load settings from default profile in database, if it exists
        #
        validator.load(self._load_config_from_database())

        #
        # Load settings from a specific profile, if one was specified
        #
        if profile and profile != 'Default':
            validator.load(self._load_config_from_database(profile))

        #
        # Validate the settings
        #
        validator.validate()

        return validator

    def getResourceAdapterConfig(self,
                                 sectionName: str = 'Default'
                                 ) -> Dict[str, Any]:
        """
        Gets the resource adatper configuration for the specified profile.

        :param str sectionName: the reousrce adapter profile to get

        :return Dict[str, Any]: the configuration

        :raises ConfigurationError:
        :raises ResourceNotFound:

        """
        self.getLogger().debug(
            'getResourceAdapterConfig(sectionName=[{0}])'.format(
                sectionName if sectionName else '(none)'))

        #
        # Validate the settings and dump the config with transformed
        # values
        #
        try:
            validator = self.validate_config(sectionName)
            processed_config: Dict[str, Any] = validator.dump()

        except ValidationError as ex:
            raise ConfigurationError(str(ex))

        #
        # Perform any required additional processing on the config
        #
        self.process_config(processed_config)

        return processed_config

    def _load_config_from_class(self) -> Dict[str, str]:
        """
        Load the settings from the resource adapter class default values
        into the config dict, overriding what is in there already.

        :returns Dict[str, str]: the configuration

        """
        config: Dict[str, str] = {}
        for k, v in self.settings.items():
            if v.default is not None:
                config[k] = v.default

        return config

    def _load_config_from_database(self,
                                   profile: str = 'Default'
                                   ) -> Dict[str, str]:
        """
        Loads a configuration profile from the database.

        :param profile: the name of the configuration profile

        :return Dict[str, str]: the configuration

        """
        config = {}

        db_handler = ResourceAdapterConfigDbHandler()

        try:
            db_config = db_handler.get(
                self.session, self.__adaptername__, profile)

            cfg_list = ResourceAdapterConfigSchema().dump(db_config).data

            for s in cfg_list['configuration']:
                config[s['key']] = s['value']
        except ResourceNotFound:
            pass

        return config

    def process_config(self, config: Dict[str, Any]):
        """
        Override this method in subclasses to perform any additional
        processing on the config. Changes to the config are performed
        in-place (i.e. config is mutable).

        :param Dict[str, Any] config: the configuration dict

        """
        pass

    @property
    def addHostApi(self):
        """Get and cache the Add Host API"""

        if self.__addHostApi is None:
            from tortuga.addhost.addHostServerLocal \
                import AddHostServerLocal

            self.__addHostApi = AddHostServerLocal()

        return self.__addHostApi

    @property
    def nodeApi(self):
        """Get and cache the Node API"""

        if self.__nodeApi is None:
            from tortuga.node.nodeApi import NodeApi
            self.__nodeApi = NodeApi()
        return self.__nodeApi

    @property
    def osObject(self):
        """Get and cache the OS Object Factory"""

        if self.__osObject is None:
            from tortuga.os_utility import osUtility
            self.__osObject = osUtility.getOsObjectFactory()
        return self.__osObject

    @property
    def sanApi(self):
        """Internal: Get and cache the SAN API"""

        if self.__sanApi is None:
            from tortuga.san import san
            self.__sanApi = san.San()
        return self.__sanApi

    def statusMessage(self, msg: str) -> None:
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
        bhm = getOsObjectFactory().getOsBootHostManager(self._cm)

        # Write out the PXE file
        bhm.writePXEFile(
            self.session, node, hardwareprofile=hardwareprofile,
            softwareprofile=softwareprofile, localboot=False)

        # Add a DHCP lease
        bhm.addDhcpLease(node, nic)

    def removeLocalBootConfiguration(self, node: Node) -> None:
        bhm = self.osObject.getOsBootHostManager(self._cm)

        bhm.rmPXEFile(node)
        bhm.removeDhcpLease(node)

    def _pre_add_host(
            self, name: str, hwprofilename: str, swprofilename: str,
            ip: Optional[str]) -> None:
        """
        Call pre-add host component actions
        """

        kitmgr = KitActionsManager()
        kitmgr.session = self.session

        kitmgr.pre_add_host(
            hwprofilename,
            swprofilename,
            name,
            ip
        )

    @property
    def installer_public_hostname(self) -> str:
        return cm.getHost()

    @property
    def installer_public_ipaddress(self) -> str:
        return cm.getIpAddress()

    @property
    def private_dns_zone(self) -> str:
        if self.__private_dns_zone is None:
            self.__private_dns_zone = \
                ParameterApi().getParameter(
                    self.session, 'DNSZone').getValue()

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

        #
        # Default settings dict is blank
        #
        config: Dict[str, str] = {}

        #
        # Load settings from class settings definitions if any of them
        # have default values
        #
        config.update(self._load_config_from_class())

        #
        # Load settings from default profile in database, if it exists
        #
        config.update(self._load_config_from_database())

        #
        # Load node specific settings
        #
        override_config: Dict[str, Any] = {}
        if node.instance and \
                node.instance.resource_adapter_configuration and \
                node.instance.resource_adapter_configuration.name != 'Default':
            for c in node.instance.resource_adapter_configuration.configuration:
                override_config[c.key] = c.value

        config.update(override_config)

        #
        # Dump the config with transformed values. Don't bother validating
        # here, as we will consider the node already exists in it's current
        # state
        #
        try:
            validator = ConfigurationValidator(self.settings)
            validator.load(config)
            processed_config: Dict[str, Any] = validator.dump()
        except ValidationError as ex:
            raise ConfigurationError(str(ex))

        #
        # Perform any required additional processing on the config
        #
        self.process_config(processed_config)

        return processed_config

    def load_resource_adapter_config(self, session: Session,
                                     name: Optional[str] = None) \
            -> ResourceAdapterConfig:
        """
        Helper method to get resource adapter configuration

        Raises:
            ResourceNotFound
        """

        return ResourceAdapterConfigDbHandler().get(
            session,
            self.__adaptername__,
            name if name else 'Default',
        )
