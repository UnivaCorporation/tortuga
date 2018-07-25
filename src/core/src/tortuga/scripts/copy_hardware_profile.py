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

from tortuga.cli import tortugaCli
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class CopyHardwareProfileCli(tortugaCli.TortugaCli):
    def __init__(self):
        super().__init__()

    def parseArgs(self, usage=None):
        option_group_name = _('Copy Hardware Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name,
                              '--src', required=True,
                              dest='srcHardwareProfileName',
                              metavar='NAME',
                              help=_('Name of source hardware profile'))
        self.addOptionToGroup(option_group_name,
                              '--dst', required=True,
                              dest='dstHardwareProfileName',
                              metavar='NAME',
                              help=_('Name of destination hardware profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Copy an existing hardware profile'))

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl(),
                                   verify=self._verify)

        api.copyHardwareProfile(
            self.getArgs().srcHardwareProfileName,
            self.getArgs().dstHardwareProfileName)


def main():
    CopyHardwareProfileCli().run()
