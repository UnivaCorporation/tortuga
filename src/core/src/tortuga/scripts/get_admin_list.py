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

from tortuga.cli.admin import AdminCli
from tortuga.wsapi.adminWsApi import AdminWsApi


class GetAdminListCli(AdminCli):
    def parseArgs(self, usage=None):

        self.addOption('-v', '--verbose',
                       action='store_true', default=False,
                       help=_('Enable verbose output'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Return list of administrators in the Tortuga system.
"""))

        api = AdminWsApi(username=self.getUsername(),
                         password=self.getPassword(),
                         baseurl=self.getUrl())

        for admin_entry in api.getAdminList():
            result = '{0}'.format(admin_entry.getUsername())

            if self.getArgs().verbose:
                if admin_entry.getRealname() and \
                        admin_entry.getUsername() != admin_entry.getRealname():
                    result += ' ({0})'.format(admin_entry.getRealname())

                if admin_entry.getDescription():
                    result += '\n        {0}'.format(
                        admin_entry.getDescription())

            print(result)


def main():
    GetAdminListCli().run()
