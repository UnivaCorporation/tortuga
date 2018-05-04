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

from tortuga.cli.admin import AdminCli
from tortuga.objects.admin import Admin
from tortuga.wsapi.adminWsApi import AdminWsApi


class UpdateAdminCli(AdminCli):
    def parseArgs(self, usage=None):
        self.addOption('--admin-username', dest='adminUsername',
                       help=_('Username of admin.'))

        self.addOption('--admin-id', dest='adminId',
                       help=_('ID of admin.'))

        self.addOption('--admin-password', dest='adminPassword',
                       help=_('Password of admin.'))

        self.addOption('--uncrypted', dest='isCrypted',
                       help=_('Is the password crypted'), default=False,
                       action='store_false')

        self.addOption('--admin-realname', dest='adminRealname',
                       help=_('Realname of admin.'))

        self.addOption('--admin-description', dest='adminDescription',
                       help=_('Description of admin.'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Updates a administrative user settings in the Tortuga system.
"""))

        admin = Admin()
        admin.setUsername(self.getArgs().adminUsername)
        admin.setPassword(self.getArgs().adminPassword)
        admin.setRealname(self.getArgs().adminRealname)
        admin.setDescription(self.getArgs().adminDescription)

        admin.setId(self.getArgs().adminId)

        api = AdminWsApi(username=self.getUsername(),
                         password=self.getPassword(),
                         baseurl=self.getUrl())

        api.updateAdmin(admin, self.getArgs().isCrypted)


def main():
    UpdateAdminCli().run()
