#!/usr/bin/env python

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

from sqlalchemy.orm.session import Session

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.dbManager import DbManager
from tortuga.db.models.component import Component
from tortuga.db.models.hardwareProfileNetwork import HardwareProfileNetwork
from tortuga.db.models.hardwareProfileProvisioningNic import \
    HardwareProfileProvisioningNic
from tortuga.db.models.network import Network
from tortuga.db.models.networkDevice import NetworkDevice
from tortuga.db.models.nic import Nic
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.networkDevicesDbHandler import NetworkDevicesDbHandler
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.os_utility import tortugaSubprocess


class DeleteNicApp(TortugaCli):
    def parseArgs(self, usage=None):
        optionsGroupName = 'Options'

        self.addOptionGroup(optionsGroupName, None)

        self.addOptionToGroup(
            optionsGroupName,
            '--nic',
            dest='nic', required=True,
            help='Provisioning NIC to be removed')

        self.addOptionToGroup(
            optionsGroupName,
            '--no-sync',
            dest='bSync', default=True, action='store_false',
            help='Do not automatically synchronize configuration changes')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        with DbManager().session() as session:
            dbNode = NodesDbHandler().getNode(
                session, self._cm.getInstaller())

            # Validate device name
            NetworkDevicesDbHandler().getNetworkDevice(
                session, self.getArgs().nic)

            # Ensure it is a provisioning NIC that is being deleted
            dbInstallerNic: Nic = None

            for dbInstallerNic in dbNode.hardwareprofile.nics:
                if dbInstallerNic.networkdevice.name == self.getArgs().nic:
                    break
            else:
                raise NicNotFound(
                    'NIC [%s] is not a provisioning NIC' % (
                        self.getArgs().nic))

            hardwareProfiles = [
                entry.hardwareprofile
                for entry in dbInstallerNic.network.hardwareprofilenetworks
                if entry.hardwareprofile != dbNode.hardwareprofile]

            if hardwareProfiles:
                raise Exception(
                    'Hardware profile(s) are associated with this'
                    ' provisioning NIC: [%s]' % (
                        ' '.join([hp.name for hp in hardwareProfiles])))

            session.query(
                HardwareProfileNetwork).filter(
                    HardwareProfileNetwork.network == dbInstallerNic.network).\
                delete()

            session.query(HardwareProfileProvisioningNic).filter(
                HardwareProfileProvisioningNic.nic == dbInstallerNic).delete()

            dbNetworkId = dbInstallerNic.network.id

            networkDeviceId = dbInstallerNic.networkdevice.id

            session.delete(dbInstallerNic)

            session.query(Network).filter(Network.id == dbNetworkId).delete()

            self._deleteNetworkDevice(session, networkDeviceId)

            session.commit()

            bUpdated = self._updateNetworkConfig(session, dbNode)

        if bUpdated and self.getArgs().bSync:
            print('Applying changes to Tortuga...')

            cmd = 'puppet agent --onetime --no-daemonize >/dev/null 2>&1'
            tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def _deleteNetworkDevice(self, session, networkDeviceId): \
            # pylint: disable=no-self-use
        results = [
            entry for entry in session.query(HardwareProfileNetwork).filter(
                HardwareProfileNetwork.networkDeviceId == networkDeviceId)
            .all()]

        if not results:
            results = [entry for entry in session.query(Nic).filter(
                Nic.networkDeviceId == networkDeviceId).all()]

            if not results:
                session.query(NetworkDevice).filter(
                    NetworkDevice.id == networkDeviceId).delete()

    def _updateNetworkConfig(self, session: Session, dbNode: Node) -> bool:
        """
        Returns True if configuration files were changed.
        """

        bUpdated = False

        if self._componentEnabled(
                session, dbNode.softwareprofile, 'dhcpd'):
            print('Updating dhcpd configuration...')

            if dbNode.hardwareprofile.nics:
                print('Restarting dhcpd...')

                tortugaSubprocess.executeCommand('genconfig dhcpd')

                tortugaSubprocess.executeCommand('service dhcpd restart')
            else:
                print('Last provisioning NIC removed. Stopping dhcpd...')

                tortugaSubprocess.executeCommand('service dhcpd stop')

            bUpdated = True

        if self._componentEnabled(
                session, dbNode.softwareprofile, 'dns'):
            print('Updating DNS configuration...')

            tortugaSubprocess.executeCommand('genconfig dns')

            bUpdated = True

        return bUpdated

    def _componentEnabled(self, session: Session,
                          dbSoftwareProfile: SoftwareProfile,
                          componentName: str) -> Component: \
            # pylint: disable=no-self-use
        dbComponents = session.query(
            Component).filter(
                Component.name == componentName).filter(
                    Component.softwareprofiles.contains(
                        dbSoftwareProfile)).all()

        if not dbComponents:
            return None

        return dbComponents[0]


def main():
    DeleteNicApp().run()
