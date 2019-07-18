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

from tortuga.cli.admin import AdminCli
from tortuga.wsapi import adminWsApi


class AddAdminCli(AdminCli):
    """
    Add admin command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption('--admin-username', dest='adminUsername',
                       help=_('Username of new admin.'))

        self.addOption('--admin-password', dest='adminPassword',
                       help=_('Password of new admin.'))

        self.addOption('--admin-realname', dest='adminRealname',
                       help=_('(optional) Real name of new admin.'))

        self.addOption('--admin-description', dest='adminDescription',
                       help=_('(optional) Description of new admin.'))

        self.addOption('--crypted', dest='isCrypted',
                       help=_('Is the password crypted'), default=False,
                       action='store_true')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Add administrative users to the Tortuga system.'
                         ' This user does not need to match any operating'
                         ' system user'))

        api = self.configureClient(adminWsApi.AdminWsApi)
        api.addAdmin(
            self.getArgs().adminUsername,
            self.getArgs().adminPassword,
            self.getArgs().isCrypted,
            self.getArgs().adminRealname,
            self.getArgs().adminDescription)


def main():
    AddAdminCli().run()
