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

"""
Usage:
    get-component-node-list <component name>

Description:
    This script is called by the tortuga_kit_uge module for determining
    which software profiles have the UGE components enabled.
"""

import yaml

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class GetComponentNodeListCli(TortugaCli):
    def parseArgs(self, usage=None):
        self.addOption(
            '--kit-name', dest='kitName',
            help='Kit for specified component')

        self.addOption(
            'component', nargs='?'
        )

        self.addOption(
            '--expand-installer-hostname', dest='bExpandInstallerHostName',
            action='store_true', default=False,
            help='Expand installer host name placeholder'
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        comp_name = self.getArgs().component

        api = self.configureClient(SoftwareProfileWsApi)

        results = {}
        for sw_profile in api.getSoftwareProfileList():
            nodes = []

            for component in sw_profile.components:
                if not self.getArgs().kitName or \
                        component.kit.name == self.getArgs().kitName:
                    if comp_name and component.name == comp_name:
                        nodes = [node.name for node in sw_profile.nodes]
                        break

            results[sw_profile.name] = nodes

        print(yaml.safe_dump(results), end=' ')


def main():
    GetComponentNodeListCli().run()
