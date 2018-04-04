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

from tortuga.admin.adminCli import AdminCli
from tortuga.wsapi import adminWsApi


class AddAdminCli(AdminCli):
    """
    Add admin command line interface.
    """

    def __init__(self):
        AdminCli.__init__(self)

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

    def runCommand(self):
        self.parseArgs(_("""
    add-admin  --admin-username=ADMINUSERNAME
       --admin-password=ADMINPASSWORD [ --crypted ]
       --admin-realname=ADMINREALNAME
       --admin-description=ADMINDESCRIPTION

Description:
    The add-admin tool adds a single administrative user to  the  Tortuga
    system.   This user does not need to match any operating system user.
"""))

        api = adminWsApi.AdminWsApi(username=self.getUsername(),
                                    password=self.getPassword(),
                                    baseurl=self.getUrl())

        api.addAdmin(
            self.getArgs().adminUsername,
            self.getArgs().adminPassword,
            self._options.isCrypted,
            self.getArgs().adminRealname,
            self.getArgs().adminDescription)


def main():
    AddAdminCli().run()
