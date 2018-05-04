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

from tortuga.kit.kitCli import KitCli
from tortuga.wsapi.kitWsApi import KitWsApi


class GetKitListCli(KitCli):
    """
    Get kit command line interface.
    """

    def runCommand(self):
        self.addOptionGroup('Display Options', '')

        self.addOptionToGroup('Display Options', '--os',
                              help='Display OS kits only',
                              action='store_true',
                              default=False,
                              dest='osonly')

        self.parseArgs(_("""
Returns the list of kits available in the system.
"""))

        api = KitWsApi(username=self.getUsername(),
                       password=self.getPassword(),
                       baseurl=self.getUrl())

        kitList = [
            str(kit) for kit in api.getKitList()
            if not self.getArgs().osonly or
            (self.getArgs().osonly and kit.getIsOs())
        ]

        kitList.sort()

        if not kitList:
            return

        print('\n'.join(kitList))


def main():
    GetKitListCli().run()
