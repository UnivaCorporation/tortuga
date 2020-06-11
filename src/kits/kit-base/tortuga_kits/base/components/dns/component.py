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

from logging import getLogger
import os

from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.kit.installer import ComponentInstallerBase
from tortuga.exceptions.parameterNotFound import ParameterNotFound


logger = getLogger(__name__)


class DnsProvider(object):
    """
    Base class for Tortuga DNS providers.
    """
    def __init__(self, private_dns_zone):
        """
        :param private_dns_zone: String
        :returns: DnsProvider
        """
        self.private_dns_zone = private_dns_zone

    def add_record(self, name, ip):
        """
        Overwrite in inheriting class.
        Write individual records into the
        DNS config.

        :returns: None

        """
        raise NotImplementedError

    def remove_record(self, name):
        """
        Remove a single record.

        :param name:
        :return:

        """
        raise NotImplementedError


class DnsmasqDnsProvider(DnsProvider):
    """
    Provide DNS server with DNSMASQ.
    """
    hostsdir = '/opt/tortuga/config/dnsmasq'

    def __init__(self, private_dns_zone):
        """
        :param private_dns_zone: String
        :returns: DnsmasqDnsProvider

        """
        super(DnsmasqDnsProvider, self).__init__(private_dns_zone)
        if not os.path.exists(self.hostsdir):
            os.mkdir(self.hostsdir, mode=0o755)

    def add_record(self, name, ip):
        hosts_file_path = os.path.join(self.hostsdir, name)
        with open(hosts_file_path, 'w') as fp:
            fp.write('{} {}\n'.format(ip, name))

    def remove_record(self, name):
        hosts_file_path = os.path.join(self.hostsdir, name)
        if os.path.exists(hosts_file_path):
            os.remove(hosts_file_path)


class ComponentInstaller(ComponentInstallerBase):
    """
    Tortuga DNS component.

    """
    name = 'dns'
    version = '7.1.0'
    os_list = [
        {'family': 'rhel', 'version': '6', 'arch': 'x86_64'},
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]

    def __init__(self, kit):
        """
        Initialise parent class.

        """
        super().__init__(kit)
        self._provider = None

    def action_get_puppet_args(self, db_software_profile,
                               db_hardware_profile,
                               *args, **kwargs):
        return {
            'domain': self._get_global_parameter('DNSZone')
        }

    @property
    def provider(self):
        if not self._provider:
            self._provider = DnsmasqDnsProvider(self._private_dns_zone())
        return self._provider

    def _private_dns_zone(self):
        return self._get_global_parameter('DNSZone')

    def _get_global_parameter(self, key, default=None):
        """
        Get parameter from the DB.

        :param key: String
        :param default: String
        :returns: DbObject
        """
        try:
            return GlobalParameterDbApi().getParameter(
                self.kit_installer.session, key).getValue()
        except ParameterNotFound:
            return default

    def _provisioning_nics(self, provisioning_nic):
        """
        Write provisioning NIC entries.

        :param provisioning_nic: Object
        :returns: None
        """

        private_dns_zone = self._private_dns_zone()

        # write record for installer host name and private zone
        self.provider.add_record(
            '{}.{}'.format(
                provisioning_nic.node.name.split('.', 1)[0], private_dns_zone),
            provisioning_nic.ip
        )

        for nic in provisioning_nic.network.nics:
            if nic == provisioning_nic:
                continue  # already handled

            if nic.node.hardwareprofile.location == 'remote' and \
                    not nic.boot:
                continue

            if nic.node.state == 'Deleted':
                continue

            self.provider.add_record(
                nic.node.name,
                nic.ip
            )

    def _node_nics(self, session):
        """
        Write compute node NIC entries.

        :param session: Object session
        :returns: None
        """

        hardware_profiles = session.query(HardwareProfile).filter(
            HardwareProfile.location != 'local'
        ).all()

        for profile in hardware_profiles:
            for node in profile.nodes:
                if not node.nics:
                    continue

                nics = {
                    'internal': [],
                    'external': []
                }

                for nic in node.nics:
                    if nic.boot:
                        nics['internal'].append(nic)
                    else:
                        nics['external'].append(nic)

                if nics['internal'] and nics['external']:
                    if profile.location == 'remote':
                        ip = nics['external'][0].ip
                    else:
                        ip = nics['internal'][0].ip

                elif nics['external'] and not nics['internal']:
                    ip = nics['external'][0].ip

                elif nics['internal'] and not nics['external']:
                    ip = nics['internal'][0].ip

                else:
                    continue

                if ip is None:
                    continue

                if node.state == 'Deleted':
                    continue

                self.provider.add_record(
                    node.name,
                    ip
                )

    def _configure(self, software_profile_name, fd, *args, **kwargs):
        """
        Shim for unused arguments.

        :param softwareProfileName:
        :param fd:
        :param *args:
        :param **kwargs:
        :returns: None
        """
        self.action_configure(software_profile_name, *args, **kwargs)

    def action_post_install(self, *args, **kwargs):
        """
        Called post install.

        :returns: None
        """
        self.action_configure(None)

    def action_configure(self, _, *args, **kwargs):
        """
        Configure.

        :param _: Unused
        :param args: Unused
        :param kwargs: Unused
        :returns: None
        """
        installer_node = NodesDbHandler().getNode(
            self.kit_installer.session,
            self.kit_installer.config_manager.getInstaller()
        )

        for provisioning_nic in installer_node.hardwareprofile.nics:
            self._provisioning_nics(provisioning_nic)

        self._node_nics(self.kit_installer.session)

    def action_pre_add_host(self, hardware_profile, software_profile,
                            hostname, ip, *args, **kwargs):
        """
        Called before hosts are added.

        :param hardware_profile: Hardware profile name
        :param software_profile: Software profile name
        :param hostname: String hostname
        :param ip: String ip address

        :returns: None
        """
        self.provider.add_record(hostname, ip)

    def action_delete_host(self, hardware_profile_name,
                           software_profile_name, nodes, *args, **kwargs):
        """
        Called before hosts are added.

        :param hardware_profile_name: String hardware profile name
        :param software_profile_name: String software profile name
        :param nodes: List Objects

        :returns: None
        """
        for node in nodes:
            self.provider.remove_record(node)
