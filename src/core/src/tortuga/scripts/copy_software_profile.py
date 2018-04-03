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
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class CopySoftwareProfileCli(tortugaCli.TortugaCli):
    def __init__(self):
        super().__init__()
        option_group_name = _('Copy Software Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name,
                              '--src',
                              dest='srcSoftwareProfileName',
                              metavar='SOFTWAREPROFILENAME',
                              help=_('Name of source software profile'))
        self.addOptionToGroup(option_group_name,
                              '--dst',
                              dest='dstSoftwareProfileName',
                              metavar='SOFTWAREPROFILENAME',
                              help=_('Name of destination software profile'))

    def runCommand(self):
        self.parseArgs(_("""
    copy-software-profile --src SOFTWAREPROFILENAME --dst SOFTWAREPROFILENAME

Description:
    Copy an existing software profile.

    Note: This does not copy the enabled components (the exception being
    the OS and base kits).

    Additional components can be queried individually using get-component-list
    and enabled using enable-component
"""))

        if self.getOptions().srcSoftwareProfileName is None or \
           self.getOptions().dstSoftwareProfileName is None:
            self.usage()

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.copySoftwareProfile(
            self.getOptions().srcSoftwareProfileName,
            self.getOptions().dstSoftwareProfileName)


def main():
    CopySoftwareProfileCli().run()
