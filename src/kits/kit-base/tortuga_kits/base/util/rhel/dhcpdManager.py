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

import os
import shutil
import platform
from jinja2 import Template

from tortuga.os_objects.osObjectManager import OsObjectManager
from tortuga.os_utility.osUtility import getNativeOsFamilyInfo


class DhcpdManager(OsObjectManager):
    """
    RHEL dhcpd manager.
    """

    SERVICE_CONFIG_FILE = '/etc/dhcpd.conf'
    SERVICE_NAME = 'dhcpd'

    def getServiceName(self):   # pylint: disable=no-self-use
        """ Get service name. """
        return DhcpdManager.SERVICE_NAME

    def getConfigFileName(self):
        # Get the DHCP configuration filename. It differs between RHEL 5.x
        # and RHEL 6.x

        vals = platform.dist()

        # Extract the platform 'version'
        vers = vals[1].split('.', 1)

        if int(vers[0]) < 6:
            # RHEL 5.x
            return self.SERVICE_CONFIG_FILE

        # RHEL 6.x
        return '/etc/dhcp/dhcpd.conf'

    def configure(self, leaseTime, dnsDomain, dnsServers, dhcpSubnets,
                  installerNode, bUpdateSysconfig=False,
                  kit_settings=None):
        '''
        Invoked on the Installer Node to (re)configure the component
        '''

        kit_settings = kit_settings or {}

        filename = self.getConfigFileName()

        # Generate static portion of dhcpd configuration file from
        # template

        dhcpCfgDict = {
            'leaseTime': leaseTime,
            'dnsDomain': dnsDomain,
            'rhel6': False,
        }

        self._logger.debug('Writing [%s]' % (filename))

        with open(filename, 'w') as fd:
            # Write the header created from template
            with open('/opt/tortuga/config/dhcpd.conf.tmpl') as fp:
                tmpl = fp.read()

            fd.write(Template(tmpl).render(dhcpCfgDict))

            for network, dhcpSubnet in dhcpSubnets.items():
                # Find DNS server on this subnet
                dnsServer = self._getDnsServerForNetwork(network, dnsServers)

                self.getLogger().debug(
                    'Configuring DHCP network [%s]' % (network))

                values = {
                    'network': network.network_address,
                    'netmask': network.netmask,
                    'gateway': dhcpSubnet['gateway'],
                }

                # Generate the section of the file for this network
                fd.write('''
subnet %(network)s netmask %(netmask)s {
    option routers             %(gateway)s;
    option subnet-mask         %(netmask)s;
''' % (values))

                if 'disable_services' in kit_settings and \
                        'ntpd' not in kit_settings['disable_services']:
                    # Only add the entry for DHCP option 'ntp-servers' if
                    # this service is enabled.

                    fd.write('    option ntp-servers         %s;\n' % (
                        dhcpSubnet['gateway']))

                if dnsServer:
                    fd.write(
                        '    option domain-name-servers %s;\n' % (dnsServer))

                fd.write('    next-server                %s;\n' % (
                    dhcpSubnet['installerIp']))

                fd.write('}\n')

                # Generate host entries for each node in the subnet
                for node in dhcpSubnet['nodes']:
                    fd.write(self._createDhcpNodeEntry(node))

        if bUpdateSysconfig:
            self.__updateSysconfig(installerNode)

    def _getDnsServerForNetwork(self, network, dnsServers): \
            # pylint: disable=no-self-use
        for dnsServer in dnsServers:
            if dnsServer in network:
                break
        else:
            dnsServer = None

        return dnsServer

    def _createDhcpNodeEntry(self, node):
            # pylint: disable=no-self-use
        entry = '''
host %(hostname)s {
    hardware ethernet %(mac)s;
''' % (node)

        if not node['unmanaged']:
            entry += '    option host-name "%s";\n' % (node['fqdn'])
            entry += '    fixed-address %s;\n' % (node['ip'])
        else:
            entry += '    ignore booting;\n'

        entry += '}\n'

        return entry

    def __getProvisioningNicDeviceNames(self, installerNode): \
            # pylint: disable=no-self-use
        return [nic.getNetworkDevice().getName()
                for nic in installerNode.getNics()
                if nic.getNetwork().getType() == 'provision']

    def __updateSysconfig(self, installerNode):
        maj_version = \
            int(getNativeOsFamilyInfo().getVersion().split('.', 1)[0])

        if maj_version > 6:
            # /etc/sysconfig/dhcpd does not apply on RHEL/CentOS 7
            return

        cfgFileName = '/etc/sysconfig/dhcpd'

        self.getLogger().debug('[dhcpd] Updating %s' % (cfgFileName))

        dhcpdNics = self.__getProvisioningNicDeviceNames(installerNode)

        with open(cfgFileName + '.NEW', 'w') as fOut:
            if not os.path.exists(cfgFileName):
                updatedEntry = 'DHCPDARGS="%s"\n' % ' '.join(dhcpdNics)

                fOut.write(updatedEntry)
            else:
                with open(cfgFileName) as fIn:
                    bFound = False

                    updatedEntry = 'DHCPDARGS="%s"\n' % ' '.join(dhcpdNics)

                    for line in fIn.readlines():
                        if line.startswith('DHCPDARGS='):
                            fOut.write(updatedEntry)

                            bFound = True
                        else:
                            fOut.write(line)

                    if not bFound:
                        fOut.write(updatedEntry)

        # Copy updated file over existing file
        shutil.copyfile(cfgFileName + '.NEW', cfgFileName)

        # Remove temporary updated file
        os.unlink(cfgFileName + '.NEW')
