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

from tortuga.admin.adminCli import AdminCli
from tortuga.wsapi.adminWsApi import AdminWsApi


class DeleteAdminCli(AdminCli):
    def parseArgs(self, usage=None):
        excl_group = self.getParser().add_mutually_exclusive_group(required=True)

        excl_group.add_argument('--admin-username', dest='adminUsername',
                                help=_('Username of admin to delete.'))

        excl_group.add_argument('--admin-id', dest='adminId',
                                help=_('ID of admin to delete.'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Deletes administrative user from Tortuga'))

        api = AdminWsApi(username=self.getUsername(),
                         password=self.getPassword(),
                         baseurl=self.getUrl())

        api.deleteAdmin(
            self.getArgs().adminId or self.getArgs().adminUsername)


def main():
    DeleteAdminCli().run()
