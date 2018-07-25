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


class GetSoftwareProfileNodesCli(TortugaCli):
    """
    Get software profile command line interface.
    """

    def parseArgs(self, usage=None):
        software_profile_attr_group = _('Software Profile Attribute Options')

        self.addOptionGroup(
            software_profile_attr_group,
            _('Software profile name must be specified.'))

        self.addOptionToGroup(
            software_profile_attr_group,
            '--software-profile', required=True,
            metavar='NAME',
            dest='softwareProfile',
            help=_('software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Return list of nodes that are using the specified software profile.
"""))

        software_profile_name = self.getArgs().softwareProfile

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl(),
                                   verify=self._verify)

        for node in api.getNodeList(software_profile_name):
            print(str(node))


def main():
    GetSoftwareProfileNodesCli().run()
