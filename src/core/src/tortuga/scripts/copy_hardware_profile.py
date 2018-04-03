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

# pylint: disable=no-member

from tortuga.cli import tortugaCli
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class CopyHardwareProfileCli(tortugaCli.TortugaCli):
    def __init__(self):
        super().__init__()
        option_group_name = _('Copy Hardware Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name,
                              '--src',
                              dest='srcHardwareProfileName',
                              metavar='HARDWAREPROFILENAME',
                              help=_('Name of source hardware profile'))
        self.addOptionToGroup(option_group_name,
                              '--dst',
                              dest='dstHardwareProfileName',
                              metavar='HARDWAREPROFILENAME',
                              help=_('Name of destination hardware profile'))

    def runCommand(self):
        self.parseArgs(_("""
    copy-hardware-profile --src HARDWAREPROFILENAME --dst HARDWAREPROFILENAME

Description:
    Copy an existing hardware profile.
"""))

        if self.getOptions().srcHardwareProfileName is None or \
                self.getOptions().dstHardwareProfileName is None:
            self.usage()

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.copyHardwareProfile(
            self.getOptions().srcHardwareProfileName,
            self.getOptions().dstHardwareProfileName)


def main():
    CopyHardwareProfileCli().run()
