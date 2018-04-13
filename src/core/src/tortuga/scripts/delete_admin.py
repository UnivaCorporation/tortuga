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
    def __init__(self):
        super().__init__()

        self.addOption('--admin-username', dest='adminUsername',
                       help=_('Username of admin to delete.'))

        self.addOption('--admin-id', dest='adminId',
                       help=_('ID of admin to delete.'))

    def runCommand(self):
        self.parseArgs(_("""
    delete-admin <--admin-username=ADMINUSERNAME|--admin-id=ADMINID>

Description:
    The delete-admin tool deletes a single administrative user  from  the
    Tortuga system.  This user does not need to match any operating sys-
    tem user.
"""))

        if not self.getArgs().adminUsername and \
                not self.getArgs().adminId:
            self.getParser().error(_('Missing Admin Username or id'))

        api = AdminWsApi(username=self.getUsername(),
                         password=self.getPassword(),
                         baseurl=self.getUrl())

        api.deleteAdmin(
            self.getArgs().adminId or self.getArgs().adminUsername)


def main():
    DeleteAdminCli().run()
