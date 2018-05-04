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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class DeleteProfileMappingCli(TortugaCli):
    """
    Get software uses hardware command line interface.
    """

    def parseArgs(self, usage=None):
        software_uses_hardware_attr_group = \
            _('Software Uses Hardware Attribute Options')

        self.addOptionGroup(
            software_uses_hardware_attr_group,
            _('Software and hardware profile ID must be specified.'))

        self.addOptionToGroup(
            software_uses_hardware_attr_group, '--software-profile',
            dest='swprofile', metavar='NAME', required=True,
            help=_('software profile'))

        self.addOptionToGroup(
            software_uses_hardware_attr_group, '--hardware-profile',
            dest='hwprofile', metavar='NAME', required=True,
            help=_('hardware profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Adjust "software uses hardware" attribute on a software  profile.
"""))

        swprofile_name = self.getArgs().swprofile
        hwprofile_name = self.getArgs().hwprofile

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.deleteUsableHardwareProfileFromSoftwareProfile(
            hwprofile_name, swprofile_name)


def main():
    DeleteProfileMappingCli().run()
