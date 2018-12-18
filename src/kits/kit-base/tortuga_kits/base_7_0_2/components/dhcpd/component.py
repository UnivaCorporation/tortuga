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

import configparser
import ipaddress
import os
import shutil
from logging import getLogger

from tortuga.config.configManager import ConfigManager
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.db.networksDbHandler import NetworksDbHandler
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.kit.installer import ComponentInstallerBase
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.node.nodeApi import NodeApi


logger = getLogger(__name__)


class DhcpProvider(object):
    """
    Base class for Tortuga DHCP providers.
    """
    def __init__(self, component_installer):
        """
        :param component_installer: Kit installer object
        :returns: DhcpProvider
        """
        self._service_name = None
        self._service_handle = getOsObjectFactory().getOsServiceManager()
        self._component_installer = component_installer

    def add_record(self):
        """
        Overwrite in inheriting class.
        Write individual records into the
        DNS config.

        :returns: None
        """
        raise NotImplementedError

    def write(self):
        """
        Overwrite in inheriting class.
        Write the complete config file out.

        :returns: None
        """
        raise NotImplementedError

    def start_service(self):
        """
        Start the service.

        :returns: None
        """
        self._service_handle.start(self._service_name)

    def stop_service(self):
        """
        Stop the servce.

        :returns: None
        """
        self._service_handle.stop(self._service_name)

    def restart_service(self):
        """
        Restart the service.

        :returns: None
        """
        self._service_handle.restart(self._service_name)


class DhcpdDhcpProvider(DhcpProvider):
    """
    Provide DHCP server with DHCPD.
    """
    def __init__(self, component_installer):
        """
        :param component_installer: Component installer instance
        :returns: DnsmasqDhcpProvider
        """
        self._service_name = 'dhcpd'
        super().__init__(component_installer)

    def write(self):
        """
        :returns: None
        """
        file_name = 'dhcpd.conf.tmpl'
        path = {
            'source': os.path.join(
                self._component_installer.files_path,
                file_name
            ),
            'destination': os.path.join(
                self._component_installer._config.getKitConfigBase(),
                file_name
            )
        }

        if os.path.isfile(path['destination']):
            if not os.path.isfile(path['destination'] + '.original'):
                shutil.copyfile(
                    path['destination'],
                    path['destination'] + '.original'
                )

        shutil.copyfile(path['source'], path['destination'])
        logger.debug('[{}] Copied [{}] to [{}]'.format(
            self._service_name,
            path['source'],
            path['destination']
        ))


class ComponentInstaller(ComponentInstallerBase):
    """
    Tortuga DHCP component.

    """
    name = 'dhcpd'
    version = '7.0.2'
    os_list = [
        {'family': 'rhel', 'version': '6', 'arch': 'x86_64'},
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]
    installer_only = True

    def __init__(self, kit):
        """
        Initialise parent class.
        """
        super().__init__(kit)

        self._provider = DhcpdDhcpProvider(self)
        self._manager = self._get_os_dhcpd_manager('dhcpd')
        self._config = ConfigManager()

    def _get_os_dhcpd_manager(self, name):
        """
        Get dhcpd manager for the appropriate os.

        :param name: the name of the dhcpd manager to get
        :returns:    the dhcpd manager instance

        """
        dir_name = '{}/util'.format(self.kit_installer.kit_path)
        dhcpd_manager = \
            getOsObjectFactory().getOsKitApplicationManager(name, dir_name)
        return dhcpd_manager

    def _get_provisioning_networks(self):
        """
        Get provisioning networks.

        :returns: Generator provisioning networks
        """
        for network in NetworksDbHandler().getNetworkList(self.session):
            if network.type == 'provision':
                yield network

    def _get_provisioning_nics(self, node):
        """
        Get provisioning nics.

        :param node: Node object
        :returns: Generator nics
        """
        for nic in node.getNics():
            if nic.getNetwork().getType() == 'provision':
                yield nic

    def _get_provisioning_nics_ip(self, node):
        """
        Get provisioning nics IP addresses.

        :param node: Node object
        :returns: Generator IPv4Address
        """
        for nic in self._get_provisioning_nics(node):
            yield ipaddress.IPv4Address(nic.getIp())

    @staticmethod
    def _get_local_nics(nics):
        """
        Get valid NICs.

        :returns: Generator nics
        """
        for nic in nics:
            if nic.boot and nic.mac:
                yield nic

    def _get_installer_ip(self, network_id):
        """
        Return IP address of provisioning interface on installer

        :raises NicNotFound:

        """

        installer_node = NodeApi().getInstallerNode(self.session)

        prov_nics = self._get_provisioning_nics(installer_node)
        for prov_nic in prov_nics:
            if prov_nic.getNetwork().getId() == network_id:
                return ipaddress.IPv4Address(prov_nic.getIp())
        raise NicNotFound(
            'Network has no corresponding provisioning NIC on installer')

    def _dhcp_subnets(self):
        """
        DHCP subnet dictionary.

        :returns: Dictionary IPv4Network network address IPv4Network subnet
        """
        subnets = {}

        for network in self._get_provisioning_networks():
            subnet = {'nodes': []}
            installer_ip = self._get_installer_ip(network.id)
            subnet['installerIp'] = installer_ip

            if not network.gateway:
                logger.info(
                    '[dhcpd] Gateway not defined for network [{}/{}], using'
                    ' IP [{}]'.format(
                        network.address,
                        network.netmask,
                        installer_ip
                    )
                )

                subnet['gateway'] = installer_ip
            else:
                subnet['gateway'] = network.gateway

            for nic in self._get_local_nics(network.nics):
                node = nic.node
                if node.hardwareprofile.location != 'local' \
                        or node.state == 'Deleted' \
                        or node.name == self._config.getInstaller():
                    continue

                node = {
                    'ip': nic.ip,
                    'mac': nic.mac,
                    'fqdn': node.name,
                    'hostname': node.name.split('.', 1)[0],
                    'unmanaged': False
                }

                subnet['nodes'].append(node)

            subnet_address = ipaddress.IPv4Network('{}/{}'.format(
                network.address,
                network.netmask
            ))

            subnets[subnet_address] = subnet

        return subnets

    @property
    def _get_kit_settings_dictionary(self):
        """
        :returns: Dictionary
        """
        settings = {}

        config = configparser.ConfigParser()
        config.read(os.path.join(
            self._config.getKitConfigBase(),
            'tortuga.ini'
        ))

        if config.has_section('tortuga_kit_base'):
            if config.has_option('tortuga_kit_base', 'disable_services'):
                settings['disable_services'] = \
                    config.get('tortuga_kit_base', 'disable_services') \
                    .split(' ')

        return settings

    def _configure(self, softwareProfileName, fd, *args, **kwargs):
        """
        Shim for unused arguments.

        :param softwareProfileName:
        :param fd:
        :param *args:
        :param **kwargs:
        :returns: None
        """
        self.action_configure(softwareProfileName, *args, **kwargs)

    def action_configure(self, _, *args, **kwargs):
        """
        Configure.

        :param _: Unused
        :param *args: Unused
        :param **kwargs: Unused
        :returns: None
        """

        try:
            result = GlobalParameterDbApi().getParameter(
                self.session,
                'DHCPLeaseTime'
            )

            dhcp_lease_time = int(result.getValue())
        except ParameterNotFound:
            dhcp_lease_time = 2400

        try:
            result = GlobalParameterDbApi().getParameter(
                self.session,
                'DNSZone')

            dns_zone = result.getValue()
        except ParameterNotFound:
            dns_zone = ''

        installer_node = NodeApi().getInstallerNode(self.session)

        self._manager.configure(
            dhcp_lease_time,
            dns_zone,
            self._get_provisioning_nics_ip(installer_node),
            self._dhcp_subnets(),
            installerNode=installer_node,
            bUpdateSysconfig=kwargs.get('bUpdateSysconfig', True),
            kit_settings=self._get_kit_settings_dictionary
        )

    def action_post_install(self, *args, **kwargs):
        """
        Triggered post install.

        :param *args: List Objects
        :param **kwargs: Dictionary Objects
        :returns: None
        """
        self._provider.write()
        self.action_configure(None, args, kwargs, bUpdateSysconfig=True)

    def action_add_host(self, hardware_profile_name, software_profile_name,
                        nodes, *args, **kwargs):
        """
        Triggerd at add host.

        :returns: None
        """
        self.action_configure(
            software_profile_name,
            None,
            args,
            kwargs,
            bUpdateSysconfig=False
        )

    def action_delete_host(self, hardware_profile_name, software_profile_name,
                           nodes, *args, **kwargs):
        """
        Triggered delete host.

        :returns: None
        """
        self.action_configure(
            software_profile_name,
            None,
            args,
            kwargs,
            bUpdateSysconfig=False
        )
