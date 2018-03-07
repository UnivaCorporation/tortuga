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

from jinja2 import Template

from tortuga.db.dbManager import DbManager
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.hardwareProfiles import HardwareProfiles
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.kit.installer import ComponentInstallerBase
from tortuga.exceptions.parameterNotFound import ParameterNotFound


logger = getLogger(__name__)


DNSMASQ_CONFIG_TEMPLATE = """
# Tortuga DNS Config

domain={{ domain }}
local=/{{ domain }}/

{% for host_record in host_records %}
host-record={{ host_record.hostname }},{{ host_record.ip }}
{% endfor %}
"""


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
        self.host_records = []

    def add_record(self, name, ip, record_type='A'):
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


class DnsmasqDnsProvider(DnsProvider):
    """
    Provide DNS server with DNSMASQ.
    """
    def __init__(self, private_dns_zone):
        """
        :param private_dns_zone: String
        :returns: DnsmasqDnsProvider
        """
        super(DnsmasqDnsProvider, self).__init__(private_dns_zone)
        self._service_handle = getOsObjectFactory().getOsServiceManager()
        self._service_name = 'dnsmasq'

    def _add_a_record(self, name, ip):
        """
        Add A record type.

        :param name: String hostname
        :param ip: String ip address
        :returns: None
        """
        self.host_records.append({
            'hostname': name,
            'ip': ip,
        })

    def _add_aaaa_record(self, name, ip):
        """
        Add AAAA record type.

        :param name: String hostname
        :param ip: String ip address
        :returns: None
        """
        raise NotImplementedError

    def start_service(self):
        """
        Start the DNSMASQ service.

        :returns: None
        """
        self._service_handle.start(self._service_name)

    def stop_service(self):
        """
        Stop the DNSMASQ servce.

        :returns: None
        """
        self._service_handle.stop(self._service_name)

    def restart_service(self):
        """
        Restart the DNSMASQ service.

        :returns: None
        """
        self._service_handle.restart(self._service_name)

    def add_record(self, name, ip, record_type='A'):
        """
        Write individual records into the
        DNS config.

        :returns: None
        """
        record_types = {
            'A': self._add_a_record,
            'AAAA': self._add_aaaa_record
        }

        try:
            record_types[record_type](name, ip)
        except IndexError:
            raise NotImplementedError(
                'Record type {} is not implemented'.format(record_type)
            )

    def write(self):
        """
        Write the complete config file out.

        :returns: None
        """
        template = Template(DNSMASQ_CONFIG_TEMPLATE)

        context = {
            'domain': self.private_dns_zone,
            'host_records': self.host_records
        }

        rendered = template.render(context)
        with open('/etc/dnsmasq.d/tortuga-dns.conf', 'w') as fp:
            fp.write(rendered)


class ComponentInstaller(ComponentInstallerBase):
    """
    Tortuga DNS component.

    """
    name = 'dns'
    version = '6.3.0'
    os_list = [
        {'family': 'rhel', 'version': '6', 'arch': 'x86_64'},
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]

    def __init__(self, kit):
        """
        Initialise parent class.
        """
        super().__init__(kit)
        self.provider = DnsmasqDnsProvider(self._private_dns_zone)

    @staticmethod
    def _get_global_parameter(key, default=None):
        """
        Get parameter from the DB.

        :param key: String
        :param default: String
        :returns: DbObject
        """
        try:
            return GlobalParameterDbApi().getParameter(key).getValue()
        except ParameterNotFound:
            return default

    @property
    def _private_dns_zone(self):
        return self._get_global_parameter('DNSZone')

    def _provisioning_nics(self, provisioning_nic):
        """
        Write provisioning NIC entries.

        :param provisioning_nic: Object
        :returns: None
        """
        # write record for installer host name and private zone
        self.provider.add_record(
            '{}.{}'.format(provisioning_nic.node.name.split('.', 1)[0],
                           self._private_dns_zone),
            provisioning_nic.ip
        )

        for nic in provisioning_nic.network.nics:
            if nic == provisioning_nic:
                continue  # already handled

            if nic.node.hardwareprofile.location == 'remote' and \
                    not nic.boot:
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

        hardware_profiles = session.query(HardwareProfiles).filter(
            HardwareProfiles.location != 'local'
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
        self.provider.write()

    def action_configure(self, _, *args, **kwargs):
        """
        Configure.

        :param _: Unused
        :param *args: Unused
        :param **kwargs: Unused
        :returns: None
        """
        with DbManager().session() as session:
            installer_node = NodesDbHandler().getNode(
                session,
                self.kit_installer.config_manager.getInstaller()
            )

            for provisioning_nic in installer_node.hardwareprofile.nics:
                self._provisioning_nics(provisioning_nic)

            self._node_nics(session)

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
        self.action_configure(None)
        self.provider.add_record(hostname, ip)
        self.provider.write()
        self.provider.restart_service()

    def action_delete_host(self, hardware_profile_name,
                           software_profile_name, nodes, *args, **kwargs):
        """
        Called before hosts are added.

        :param hardware_profile_name: String hardware profile name
        :param software_profile_name: String software profile name
        :param nodes: List Objects

        :returns: None
        """
        self.action_configure(None)
        self.provider.write()
        self.provider.restart_service()
