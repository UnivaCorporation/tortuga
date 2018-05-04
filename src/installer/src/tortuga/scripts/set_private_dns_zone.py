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

# pylint: disable=multiple-statements,not-callable,no-member

import sys
import os
import shutil
import configparser
import yaml

from sqlalchemy.orm.exc import NoResultFound

from tortuga.os_utility import tortugaSubprocess
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.models.globalParameter import GlobalParameter
from tortuga.db.dbManager import DbManager
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.db.nodesDbHandler import NodesDbHandler


class SetPrivateDnsZoneApp(TortugaCli):
    def parseArgs(self, usage=None):
        self.addOption(
            '--force', action='store_true', default='false',
            dest='bForce', help='Force update of domain name')

        self.addOption('zone', nargs='?')

        self.dbm = DbManager()

        self.dns_conf = {}

        self.cfg = configparser.ConfigParser()

        self.cfgFileName = os.path.join(
            self._cm.getRoot(), 'config/base/dns-component.conf')

        self._loadDNSConfig()

        super().parseArgs(usage=usage)

    def _loadDNSConfig(self):
        self.cfg.read(self.cfgFileName)

        # Read/parse existing DNS settings

        if self.cfg.has_section('dns'):
            if self.cfg.has_option('dns', 'domain'):
                self.dns_conf['domain'] = self.cfg.get('dns', 'domain')

            if self.cfg.has_option('dns', 'type'):
                dns_type = self.cfg.get('dns', 'type')

                self.dns_conf['type'] = dns_type

                if not self.dns_conf['type'].lower() in ('named', 'dnsmasq'):
                    # Invalid DNS type
                    self.dns_conf['type'] = 'named'
            else:
                # Default to 'named'
                self.dns_conf['type'] = 'named'

    def _getOldDnsZone(self):
        """
        Returns None if DNS zone previously undefined
        """

        return self.dns_conf['domain'] if 'domain' in self.dns_conf else None

    def _updateDatabase(self, dnsZone):

        session = self.dbm.openSession()

        dbValue = None

        try:
            dbValue = session.query(GlobalParameter).filter(
                GlobalParameter.name == 'DNSZone').one()

            # Update existing value
            dbValue.value = dnsZone
        except NoResultFound:
            pass

        if dbValue is None:
            dbValue = GlobalParameter(name='DNSZone', value=dnsZone)
            session.append(dbValue)

        session.commit()

        self.dbm.closeSession()

    def _updateDnsComponentConf(self, dnsZone):
        if os.path.exists(self.cfgFileName):
            shutil.copy(self.cfgFileName, self.cfgFileName + '.orig')

            self.cfg.set('dns', 'domain', dnsZone)

            with open(self.cfgFileName + '.modified', 'w') as fpOut:
                self.cfg.write(fpOut)

            shutil.copy(self.cfgFileName + '.modified', self.cfgFileName)

            os.unlink(self.cfgFileName + '.modified')

    def _updatePuppetExtData(self, dnsZone): \
            # pylint: disable=no-self-use
        # Read existing 'DNSZone' setting from Hiera

        fn = ('/etc/puppetlabs/code/environments/production/data'
              '/tortuga-common.yaml')

        srcDataDict = {}

        with open(fn) as fpIn:
            srcDataDict = yaml.load(fpIn)

        srcDataDict['DNSZone'] = dnsZone

        # Write updated file
        with open(fn + '.new', 'w') as fpOut:
            fpOut.write(
                yaml.safe_dump(
                    srcDataDict, default_flow_style=False,
                    explicit_start=True))

        # Move new file into place
        if not os.path.exists(fn + '.orig'):
            shutil.copyfile(fn, fn + '.orig')

        shutil.copyfile(fn + '.new', fn)

        os.unlink(fn + '.new')

    def isDnsComponentEnabled(self):
        session = self.dbm.openSession()

        dbInstallerNode = NodesDbHandler().getNode(
            session, self._cm.getInstaller())

        bDnsComponentEnabled = False

        # Iterate over components in software profile looking for one
        # matching name 'dns'
        for dbComponent in dbInstallerNode.softwareprofile.components:
            if dbComponent.name == 'dns':
                bDnsComponentEnabled = True
                break

        self.dbm.closeSession()

        return bDnsComponentEnabled

    def runCommand(self):
        self.parseArgs()

        # Remove remnants
        oldDnsZone = self._getOldDnsZone()

        dnsZone = self.getArgs().zone

        if dnsZone:
            # Output current DNS zone and exit

            sys.stdout.write('{0}\n'.format(oldDnsZone))

            sys.exit(0)

        if oldDnsZone == dnsZone.lower():
            if not self.getArgs().bForce:
                # Nothing changed. Nothing to do!
                sys.exit(0)

        # Update database
        self._updateDatabase(dnsZone)

        # Update dns-component.conf
        self._updateDnsComponentConf(dnsZone)

        # Update Puppet extdata file
        self._updatePuppetExtData(dnsZone)

        if 'type' in self.dns_conf and self.dns_conf['type'] == 'named':
            oldZoneFileName = '/var/named/%s.zone' % (oldDnsZone.lower())

            if os.path.exists(oldZoneFileName):
                # Attempt to remove old named configuration
                os.unlink(oldZoneFileName)

        bDnsComponentEnabled = self.isDnsComponentEnabled()

        # TODO: update (genconfig dns)
        if bDnsComponentEnabled:
            tortugaSubprocess.executeCommand('genconfig dns')

        # TODO: schedule puppet update
        tortugaSubprocess.executeCommand(
            'schedule-update "DNS zone changed from \"%s\" to \"%s\""' % (
                oldDnsZone, dnsZone))

        if bDnsComponentEnabled and 'type' in self.dns_conf:
            if self.dns_conf['type'] == 'named':
                cmd = 'service named restart'
            else:
                cmd = 'service dnsmasq restart'

            tortugaSubprocess.executeCommand(cmd)


def main():
    SetPrivateDnsZoneApp().run()
