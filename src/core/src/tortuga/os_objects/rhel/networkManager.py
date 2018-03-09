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

import ipaddress
import json
import re
import struct
import subprocess

from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.os_objects.osObjectManager import OsObjectManager


class NetworkManager(OsObjectManager):
    NETWORK = '/etc/sysconfig/network'
    NIC_PATTERN = '/etc/sysconfig/network-scripts/ifcfg-*'
    DNS = '/etc/resolv.conf'

    def _isNetworkManagerInUse(self):
        cmd = 'service NetworkManager status'

        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        while True:
            result = p.stdout.readline()
            if not result:
                break

        retval = p.wait()

        return retval == 0

    def findNics(self, deviceName=None):
        nicDict = {}

        ifcfgDict = self.loadIfcfgDict()

        for cfgFile, intfcDict in ifcfgDict.items():
            nic = self._get_nic_info(cfgFile, intfcDict)

            nicDict[nic['device']] = nic

        return nicDict

    def getDeviceUuidMap(self):
        """
        Use 'nmcli' to obtain the device name-to-UUID mapping
        """
        deviceUuidDict = {}

        # We can only depend on 'nmcli' being available where
        # NetworkManager is in use.
        if not self._isNetworkManagerInUse():
            return {}

        cmd = 'nmcli --terse --fields devices,uuid con status'

        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        while True:
            result = p.stdout.readline()
            if not result:
                break

            deviceName, deviceUuid = result.rstrip().split(':', 1)

            deviceUuidDict[deviceUuid] = deviceName

        retval = p.wait()
        if retval != 0:
            return {}

        return deviceUuidDict

    def _getDeviceByHwaddr(self, hwAddr):
        device = None

        cmd = ('LANG=C ip -o link | grep -v link/ieee802.11 |'
               ' awk -F \': \' -vIGNORECASE=1 "/%s/ { print \\$2 }"' % (
                   hwAddr))

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        while True:
            buf = p.stdout.readline()
            if not buf:
                break

            device = buf.rstrip()

        retval = p.wait()
        if retval != 0:
            return None

        return device

    def _getNetworkInterfaceDeviceName(self, intfcDict):
        # Get device/UUID map
        deviceUuidMap = self.getDeviceUuidMap()

        if 'DEVICE' in intfcDict:
            return intfcDict['DEVICE']

        # Device is not defined in configuration, look it up
        if 'UUID' not in intfcDict:
            return None

        uuid = intfcDict['UUID']

        if uuid in deviceUuidMap:
            return deviceUuidMap[uuid]

        # Map UUID to device name
        if 'HWADDR' not in intfcDict:
            # Unable to determine NIC device name
            return None

        return self._getDeviceByHwaddr(intfcDict['HWADDR'])

    def _getNetworkInterfaceMacAddress(self, device, intfcDict):
        macAddr = None

        if 'HWADDR' in intfcDict:
            macAddr = intfcDict['HWADDR']

        return macAddr

    def _getNetworkInterfaceBootproto(self, intfcDict):
        bootproto = 'static'

        if 'BOOTPROTO' in intfcDict:
            bootproto = intfcDict['BOOTPROTO']

        return bootproto

    def _getNetworkInterfaceOnBoot(self, intfcDict):
        onboot = None

        if 'ONBOOT' in intfcDict:
            onboot = intfcDict['ONBOOT']

        return onboot is not None and onboot.lower() == "yes"

    def _getNetworkManagerDevice(self, deviceName):
        devDict = {}

        if not self._isNetworkManagerInUse():
            return {}

        cmd = 'nmcli --terse dev list iface %s' % (deviceName)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        while True:
            result = p.stdout.readline()
            if not result:
                break

            key, value = result.rstrip().split(':', 1)

            devDict[key] = value

        retval = p.wait()
        if retval != 0:
            return {}

        return devDict

    def _get_netmask_by_network_class(self, ip):
        # Use address class to determine default netmask
        tmpIP = ipaddress.IPv4Address(str(ip))

        octets = struct.unpack('BBBB', tmpIP.packed)

        if octets[0] >= 0 and octets[0] <= 127:
            # Default Class A netmask
            return '255.0.0.0'

        if octets[0] >= 128 and octets[0] <= 191:
            # Default Class B netmask
            return '255.255.0.0'

        # Default Class C netmask
        # IP address 192.x.x.x to 254.x.x.x
        return '255.255.255.0'

    def _get_nic_info(self, cfgFile, intfcDict):
        device = self._getNetworkInterfaceDeviceName(intfcDict)
        if not device:
            # Unable to determine device name for network interface,
            # configuration may be bogus.
            self.getLogger().warning(
                'Unable to determine device name for [%s]' % (cfgFile)
            )

            return None

        ip = netmask = network = None

        devDict = self._getNetworkManagerDevice(device)
        if not devDict:
            if 'IPADDR' in intfcDict:
                ip = intfcDict['IPADDR']
            else:
                ip, netmask = self._get_interface_ip_address(device)

            if 'NETMASK' in intfcDict:
                netmask = intfcDict['NETMASK']
            else:
                # Create netmask from PREFIX
                if 'PREFIX' in intfcDict:
                    # Convert the prefix (ie /24) to a netmask
                    netmask = ipaddress.IPv4Network(
                        '%s/%s' % (ip, intfcDict['PREFIX'])).netmask
                else:
                    netmask = self._get_netmask_by_network_class(ip)
        else:
            # Use results obtained from NetworkManager
            if 'IP4-SETTINGS.ADDRESS' in devDict:
                ip = devDict['IP4-SETTINGS.ADDRESS']

            if 'IP4-SETTINGS.PREFIX' in devDict:
                vals = devDict['IP4-SETTINGS.PREFIX'].split(' ')

                netmask = vals[1][1:-1]

        if ip and netmask:
            network = str(ipaddress.IPv4Network(
                u('%s/%s' % (ip, netmask))).network)

        mac = self._getNetworkInterfaceMacAddress(device, intfcDict)
        if not mac and 'GENERAL.HWADDR' in devDict:
            mac = devDict['GENERAL.HWADDR']

        bootproto = self._getNetworkInterfaceBootproto(intfcDict)

        dhcp = (bootproto.lower() == 'dhcp')

        enabled = self._getNetworkInterfaceOnBoot(intfcDict)

        return {
            'device': device,
            'ip': ip,
            'netmask': netmask,
            'network': network,
            'mac': mac,
            'dhcp': dhcp,
            'boot': True,
            'provision': False,
            'enabled': enabled,
            'cfgfile': cfgFile,
        }

    def _get_interface_ip_address(self, name):
        try:
            p = subprocess.Popen(
                'ifconfig ' + name, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            retcode = p.wait()
            if retcode != 0:
                raise Exception(p.stderr.readline())

            line = p.stdout.readline()  # Skip the first line
            line = p.stdout.readline()  # We want the second line
            p.stdout.close()

            p = re.compile(
                r'^\s*inet addr:(?P<ip>\S+)\s+Bcast:\S+\s+'
                r'Mask:(?P<mask>\S+)\s*$')
            m = p.match(line)
            if not m:
                raise SyntaxError("Can't parse [%s]" % line.strip())

            return m.group('ip'), m.group('mask')

        except Exception as msg:
            self.getLogger().warning(
                "Warning: Can't get_interface_ip_address for [%s]: %s" % (
                    name, msg))

            return '', ''

    def getNetworkInterfaces(self):
        """
        Returns list of interfaces on installer as discovered by
        'facter interfaces'. List does not include 'lo' (loopback)
        device.

        Raises:
            NicNotFound
        """

        cmd = 'facter --json interfaces'

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        result = json.load(p.stdout)

        retval = p.wait()

        if retval != 0 or 'interfaces' not in result:
            errmsg = 'Unable to find public NIC on installer'

            self.getLogger().error('[networkManager] ' + errmsg)

            raise NicNotFound(errmsg)

        return [intfc for intfc in result['interfaces'].split(',')
                if intfc != 'lo']
