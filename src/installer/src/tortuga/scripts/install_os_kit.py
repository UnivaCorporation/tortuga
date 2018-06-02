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

from typing import List

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.kit.kitApiFactory import getKitApi
from tortuga.kit.loader import load_kits
from tortuga.puppet import Puppet


class InstallOsKitCli(TortugaCli):
    """
    Install kit command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption('-m', '--media', dest='osMediaUrl',
                       required=True, metavar='URL',
                       help=_('OS kit package URL'))

        self.addOption('--symlinks', dest='symlinksFlag',
                       help=_('Symlink media instead of copying'),
                       action='store_true', default=False)

        self.addOption('--force', action='store_true', default=False,
                       help=_('Force reinstallation of existing OS kit'))

        self.addOption('--mirror', action='store_true', default=False,
                       help=_('Specified URL is an OS repository mirror, not a'
                              ' specific OS version'))
        self.addOption('--no-sync', dest='sync', action='store_false',
                       default=True, help=_('component version'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Installs operating system media to Tortuga for the purpose of
package-based node provisioning.
"""))

        load_kits()

        api = getKitApi(self.getUsername(), self.getPassword())

        # Pre-process the media URL list
        os_media_urls: List[str] = self.getArgs().osMediaUrl.split(',')

        api.installOsKit(
            os_media_urls,
            bUseSymlinks=self.getArgs().symlinksFlag,
            bInteractive=True,
            mirror=self.getArgs().mirror
        )

        if self.getArgs().sync:
            Puppet().agent()


def main():
    InstallOsKitCli().run()
