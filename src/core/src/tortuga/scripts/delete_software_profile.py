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

import argparse
from typing import Optional

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class DeleteSoftwareProfileCli(TortugaCli):
    def parseArgs(self, usage: Optional[str] = None):
        option_group_name = _('Delete Software Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--name',
                              dest='softwareProfileName',
                              help=argparse.SUPPRESS)

        self.getParser().add_argument(
            'name', metavar='NAME',
            help=_('Name of software profile to delete'),
            nargs='?',
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Removes software profile from system.'))

        if not self.getArgs().name and \
                not self.getArgs().softwareProfileName:
            self.getParser().error(
                'the following arguments are required: NAME'
            )

        if self.getArgs().name and self.getArgs().softwareProfileName:
            self.getParser().error(
                'argument name: not allowed with argument --name'
            )

        name = self.getArgs().name \
            if self.getArgs().name else self.getArgs().softwareProfileName

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl(),
                                   verify=self._verify)

        api.deleteSoftwareProfile(name)


def main():
    DeleteSoftwareProfileCli().run()
