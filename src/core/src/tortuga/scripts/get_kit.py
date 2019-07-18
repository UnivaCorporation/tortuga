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

import json
import sys

from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.kit.kitCli import KitCli
from tortuga.wsapi.kitWsApi import KitWsApi


class GetKitCli(KitCli):
    """
    Get kit command line interface.

    """
    def parseArgs(self, usage=None):
        cmd_options_group = _('Command Options')

        self.addOptionGroup(cmd_options_group, '')
        self.addOptionToGroup(cmd_options_group, '--quiet',
                              action='store_true', dest='bQuiet',
                              help=_('Return success (0) if kit exists,'
                                     ' otherwise 1.'))

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

        super(GetKitCli, self).parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Returns details of the specified kit
"""))

        name, version, iteration = \
            self.getKitNameVersionIteration(self.getArgs().kitspec)

        api = self.configureClient(KitWsApi)

        try:
            kit = api.getKit(name, version=version, iteration=iteration)

            if not self.getArgs().bQuiet:
                if self.getArgs().xml:
                    print(kit.getXmlRep())
                elif self.getArgs().json:
                    print(json.dumps({
                        'kit': kit.getCleanDict(),
                    }, sort_keys=True, indent=4, separators=(',', ': ')))
                else:
                    self._console_output(kit)

            sys.exit(0)
        except KitNotFound:
            if self.getArgs().bQuiet:
                sys.exit(1)

            # Push the "kit not found" exception up the stack
            raise

    def _console_output(self, kit):
        print('{0}-{1}-{2}'.format(kit.getName(),
                                   kit.getVersion(),
                                   kit.getIteration()))

        print(' ' * 2 + '- Description: {0}'.format(kit.getDescription()))

        print(' ' * 2 + '- Type: {0}'.format(
            'OS' if kit.getIsOs() else 'Application'
            if kit.getName() != 'base' else 'System'))

        print(' ' * 2 + '- Removable: {0}'.format(kit.getIsRemovable()))

        print(' ' * 2 + '- Components:')

        for component in kit.getComponentList():
            print(' ' * 4 + '- Name: {0}, Version: {1}'.format(
                component.getName(), component.getVersion()))

            print(' ' * 6 + '- Description: {0}'.format(
                component.getDescription()))

            if not kit.getIsOs():
                compatible_os = component.getOsInfoList() +\
                    component.getOsFamilyInfoList()
            else:
                compatible_os = []

            if compatible_os:
                print(' ' * 6 + '- Operating system(s): {0}'.format(
                    ', '.join([str(item) for item in compatible_os])))


def main():
    GetKitCli().run()
