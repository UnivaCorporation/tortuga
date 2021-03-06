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

from typing import Optional
from tortuga.kit.kitCli import KitCli
from tortuga.wsapi.kitWsApi import KitWsApi


class DeleteKitCli(KitCli):
    """
    Delete kit command line interface.

    """

    def parseArgs(self, usage=None):
        options_attr_group = _('Options')

        self.addOptionGroup(options_attr_group, '')

        self.addOptionToGroup(options_attr_group, '--force',
                              action='store_true', default=False,
                              help=_('Forcibly remove a kit that may be in'
                                     ' use. Use with care!'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Delete installed operating system or application kit from Tortuga.
"""))

        name, version, iteration = self.get_name_version_iteration()

        api = self.configureClient(KitWsApi)
        api.deleteKit(name, version, iteration, force=self.getArgs().force)


def main():
    DeleteKitCli().run()
