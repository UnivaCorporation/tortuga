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

# Add NIC to installer after Tortuga has been installed

import os.path
import subprocess
import sys

import yaml
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.models.component import Component
from tortuga.db.dbManager import DbManager
from tortuga.db.models.component import Component
from tortuga.db.models.hardwareProfileNetwork import HardwareProfileNetwork
from tortuga.db.models.network import Network
from tortuga.db.models.networkDevice import NetworkDevice
from tortuga.db.models.nic import Nic
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.node import nodeApiFactory
from tortuga.os_utility import tortugaSubprocess


class AddNicCli(TortugaCli):
    def parseArgs(self, usage=None):
        optionsGroupName = 'Options'

        options_group = self.addOptionGroup(optionsGroupName, None)

        excl_group = options_group.add_mutually_exclusive_group(
            required=True)

        excl_group.add_argument(
            '--autodetect',
            action='store_true', default=False,
            dest='autodetect',
            help='Auto-detect unmanaged network interfaces')

        excl_group.add_argument(
            '--nic',
            dest='nic',
            help='Add provisioning NIC to installer')

        self.addOptionToGroup(
            optionsGroupName,
            '--network',
            dest='network',
            help='Network address (if autodetect does not work)')

        self.addOptionToGroup(
            optionsGroupName,
            '--netmask',
            dest='netmask',
            help='Netmask (if autodetect does not work)')

        self.addOptionToGroup(
            optionsGroupName,
            '--ip-address',
            dest='ipaddress',
            help='IP address of network interface')

        self.addOptionToGroup(
            optionsGroupName,
            '--mac-addr',
            dest='macaddress',
            help='MAC address of network interface')

        self.addOptionToGroup(
            optionsGroupName,
            '--no-sync',
            dest='bSync', default=True, action='store_false',
            help='Do not automatically synchronize configuration changes')

        self.addOptionToGroup(
            optionsGroupName,
            '--force', dest='bForce', default=False,
            action='store_true',
            help='Skip network interface validation')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs('Register provisioning network interface in Tortuga')

        with DbManager().session() as session:
            if self.getArgs().autodetect:
                self._findUnmanagedNics(session)
            elif self.getArgs().nic:
                # Attempt to automatically determine the parameters for the
                # specified NIC and associate with installer
                self._addNic(session, self.getArgs().nic)

    def _getSystemNics(self): \
            # pylint: disable=no-self-use
        cmd = '/opt/puppetlabs/bin/facter interfaces'

        p = tortugaSubprocess.TortugaSubprocess(
            cmd,
            shell=True,
            stdout=tortugaSubprocess.subprocess.PIPE,
            stderr=tortugaSubprocess.subprocess.STDOUT
        )

        results = []

        while True:
            data = p.stdout.readline()
            if not data:
                break

            results.append(data.rstrip())

        retval = p.wait()
        if retval != 0:
            raise Exception('Unable to get system network interfaces')

        return [
            str(item) for item in results[0].split(',') if item != 'lo'
        ]

    def _findUnmanagedNics(self, session: Session):
        # Get list of all NICs on the installer
        systemNics = set(self._getSystemNics())

        # Get provisioning NICs on installer
        node_api = nodeApiFactory.getNodeApi()
        nics = node_api.getInstallerNode(session).getNics()

        # Filter out the NIC names
        primaryInstallerNics = set(
            [nic.getNetworkDevice().getName() for nic in nics])

        # Determine difference between all system NICs and managed NICs
        unmanagedNics = systemNics.difference(primaryInstallerNics)

        print('The following NICs are not currently managed: %s' % (
            ' '.join(unmanagedNics)))

    def _getMultipleFacterEntries(self, entries): \
            # pylint: disable=no-self-use
        # Use 'facter' with YAML option to retrieve specified entries
        cmd = '/opt/puppetlabs/bin/facter -y %s' % (' '.join(entries))

        p = tortugaSubprocess.TortugaSubprocess(
            cmd,
            shell=True,
            stdout=tortugaSubprocess.subprocess.PIPE,
            stderr=tortugaSubprocess.subprocess.STDOUT)

        d = yaml.load(p.stdout)

        retval = p.wait()
        if retval != 0:
            return {}

        return d

    def _addNetwork(self, nicName, network, netmask, session): \
            # pylint: disable=no-self-use
        dbNetwork = Network()

        dbNetwork.address = network
        dbNetwork.netmask = netmask
        dbNetwork.type = 'provision'
        dbNetwork.name = 'Provisioning network on %s' % (nicName)
        dbNetwork.usingDhcp = False

        session.add(dbNetwork)

        return dbNetwork

    def _getNetworkDevice(self, nicName, session): \
            # pylint: disable=no-self-use
        try:
            dbNetworkDevice = session.query(
                NetworkDevice).filter(NetworkDevice.name == nicName).one()
        except NoResultFound:
            dbNetworkDevice = None

        return dbNetworkDevice

    def _addNetworkDevice(self, nicName, session): \
            # pylint: disable=no-self-use
        dbNetworkDevice = NetworkDevice(name=nicName)

        session.add(dbNetworkDevice)

        return dbNetworkDevice

    def _check_default_gateway_nic(self, nicName):
        try:
            cmd = 'ip route show 0.0.0.0/0 | awk \'{print $5}\''

            p = tortugaSubprocess.TortugaSubprocess(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            result = b''

            while True:
                buf = p.stdout.readline()
                if not buf:
                    break

                result += buf

            retval = p.wait()

            if retval != 0:
                # Unable to determine if this nic is the default gateway,
                # carry on...
                pass
            else:
                if not self.getArgs().bForce and \
                        result.decode().rstrip() == nicName:
                    print('Device [%s] is the default gateway.' % (nicName))
                    print('\nUse --force to override this warning.')

                    raise SystemExit(1)

            return
        except TortugaException:
            # This command should never fail. If it does, we just ignore
            # the result and proceed as normal.
            pass

    def _addNic(self, session, nicName):
        # Get IP address and netmask using facter

        facterNicName = nicName.replace(':', '_').replace('.', '_')

        entries = [
            'ipaddress_%s' % (facterNicName),
            'netmask_%s' % (facterNicName),
            'macaddress_%s' % (facterNicName),
            'network_%s' % (facterNicName)
        ]

        d = self._getMultipleFacterEntries(entries)

        if not 'ipaddress_%s' % (facterNicName) in d or \
           not d['ipaddress_%s' % (facterNicName)]:
            if not self.getArgs().ipaddress:
                raise InvalidCliRequest(
                    'Unable to determine IP address, use command-line'
                    ' override')

            ipaddress = self.getArgs().ipaddress
        else:
            ipaddress = d['ipaddress_%s' % (facterNicName)]

        if not 'netmask_%s' % (facterNicName) in d or \
           not d['netmask_%s' % (facterNicName)]:
            if not self.getArgs().netmask:
                raise InvalidCliRequest(
                    'Unable to determine netmask, use command-line'
                    ' override')

            netmask = self.getArgs().netmask
        else:
            netmask = d['netmask_%s' % (facterNicName)]

        if not 'network_%s' % (facterNicName) in d or \
           not d['network_%s' % (facterNicName)]:
            if not self.getArgs().network:
                raise InvalidCliRequest(
                    'Unable to determine network, use command-line'
                    ' override')

            network = self.getArgs().network
        else:
            network = d['network_%s' % (facterNicName)]

        # Check if nic is the default gateway as well...
        self._check_default_gateway_nic(nicName)

        dbNetwork = None

        # Attempt to find matching network
        try:
            dbNetwork = session.query(Network).filter(
                and_(
                    Network.address == network,
                    Network.netmask == netmask)).one()

            print('Found network [%s/%s]' % (
                dbNetwork.address, dbNetwork.netmask))
        except NoResultFound:
            # Network is not known to Tortuga, add it
            pass

        if dbNetwork is None:
            print('Adding network [%s/%s]' % (network, netmask))

            dbNetwork = self._addNetwork(nicName, network, netmask, session)

        # Attempt to find entry in NetworkDevices
        dbNetworkDevice = self._getNetworkDevice(nicName, session)
        if not dbNetworkDevice:
            # Create network device
            print('Adding network device [%s] as provisioning NIC' % (nicName))

            dbNetworkDevice = self._addNetworkDevice(nicName, session)
        else:
            print('Found existing network device [%s]' % (nicName))

        dbNode = NodesDbHandler().getNode(session, self._cm.getInstaller())

        # Attempt to find Nics entry
        for dbNic in dbNode.nics:
            if dbNic.networkdevice.name == nicName.lower():
                print('Found existing NIC entry for [%s]' % (
                    dbNic.networkdevice.name))

                break
        else:
            print('Creating NIC entry for [%s]' % (dbNetworkDevice.name))

            dbNic = Nic()
            dbNic.networkdevice = dbNetworkDevice
            dbNic.ip = ipaddress
            dbNic.boot = True
            dbNic.network = dbNetwork

            dbNode.nics.append(dbNic)

        # Attempt to find NIC association with hardware profile (commonly
        # known as hardware profile provisioning NIC)
        for dbHwProfileNic in dbNode.hardwareprofile.nics:
            if dbHwProfileNic == dbNic:
                break
        else:
            print('Adding NIC [%s] to hardware profile [%s]' % (
                dbNic.networkdevice.name, dbNode.hardwareprofile.name))

            dbNode.hardwareprofile.nics.append(dbNic)

        # Attempt to find 'HardwareProfileNetworks' entry
        for dbHardwareProfileNetwork in \
                dbNode.hardwareprofile.hardwareprofilenetworks:
            if dbHardwareProfileNetwork.network == dbNetwork and \
                dbHardwareProfileNetwork.networkdevice == dbNetworkDevice:
                print('Found existing hardware profile/network association')
                break
        else:
            dbHardwareProfileNetwork = HardwareProfileNetwork()

            dbHardwareProfileNetwork.network = dbNetwork
            dbHardwareProfileNetwork.networkdevice = dbNetworkDevice

            dbNode.hardwareprofile.hardwareprofilenetworks.append(
                dbHardwareProfileNetwork)

        session.commit()

        bUpdated = self._updateNetworkConfig(session, dbNode)

        if bUpdated and self.getArgs().bSync:
            print('Applying changes to Tortuga...')

            cmd = ('/opt/puppetlabs/bin/puppet agent --onetime'
                   ' --no-daemonize >/dev/null 2>&1')
            tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def _componentEnabled(self, session, dbSoftwareProfile, componentName): \
            # pylint: disable=no-self-use
        dbComponents = session.query(
            Component).filter(
                Component.name == componentName).filter(
                    Component.softwareprofiles.contains(
                        dbSoftwareProfile)).all()

        if not dbComponents:
            return None

        return dbComponents[0]

    def _updateNetworkConfig(self, session, dbInstallerNode):
        """
        Returns True if configuration files were changed.
        """

        bUpdated = False

        bin_dir = os.path.dirname(sys.argv[0])

        # Update dhcpd configuration
        if self._componentEnabled(
                session, dbInstallerNode.softwareprofile, 'dhcpd'):
            print('Updating dhcpd configuration...')

            tortugaSubprocess.executeCommand(
                '{} {}'.format(os.path.join(bin_dir, 'genconfig'), 'dhcpd'))

            tortugaSubprocess.executeCommand('service dhcpd restart')

            bUpdated = True

        # Update DNS configuration after adding a provisioning NIC
        if self._componentEnabled(
                session, dbInstallerNode.softwareprofile, 'dns'):
            print('Updating DNS configuration...')

            tortugaSubprocess.executeCommand(
                '{} {}'.format(os.path.join(bin_dir, 'genconfig'), 'dns'))

            # Because the entire configuration changes between before and
            # after there was a provisioning NIC installed, it is necessary
            # to restart the server. An 'rndc reload' will *NOT* suffice.
            tortugaSubprocess.executeCommandAndIgnoreFailure(
                'service named restart')

            bUpdated = True

        return bUpdated


def main():
    AddNicCli().run()
