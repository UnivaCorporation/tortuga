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

import sys

from tortuga.cli.tortugaCli import TortugaCli


class GenconfigAppClass(TortugaCli):
    def parseArgs(self, usage=None):
        self.addOption('cname')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        from tortuga.kit.actions.manager import KitActionsManager
        kitmgr = KitActionsManager()

        component = kitmgr.load_component(self.getArgs().cname)

        nodegroup = 'installer'

        if '_configure' not in dir(component):
            print(_('This component does not have configuration'),
                  file=sys.stderr)

            sys.exit(0)

        component._configure(nodegroup, sys.stdout)


def main():
    GenconfigAppClass().run()
