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

import json
from tortuga.admin.adminCli import AdminCli
from tortuga.wsapi.adminWsApi import AdminWsApi


class GetAdminCli(AdminCli):
    """
    Get admin command line interface.

    """
    def parseArgs(self, usage=None):
        self.addOption('--admin-username', required=True,
                       help=_('Username of admin to get.'))

        output_attr_group = _('Output formatting options')

        self.addOptionGroup(output_attr_group, None)

        self.addOptionToGroup(
            output_attr_group, '--json',
            action='store_true', default=False,
            help=_('JSON formatted output')
        )

        self.addOptionToGroup(
            output_attr_group, '--xml',
            action='store_true', default=False,
            help=_('XML formatted output')
        )

        super(GetAdminCli, self).parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Returns admin user from the Tortuga system.
"""))

        api = AdminWsApi(username=self.getUsername(),
                         password=self.getPassword(),
                         baseurl=self.getUrl())
        admin = api.getAdmin(self.getArgs().admin_username)

        if self.getArgs().xml:
            print(admin.getXmlRep())
        elif self.getArgs().json:
            print(json.dumps({
                'admin': admin.getCleanDict(),
            }, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            print('{0} (id: {1})'.format(admin.getUsername(), admin.getId()))

            if admin.getRealname():
                print(' ' * 2 + '- Name: {0}'.format(admin.getRealname()))

            print(' ' * 2 + '- Description: {0}'.format(admin.getDescription()))


def main():
    GetAdminCli().run()
