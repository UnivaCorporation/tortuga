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
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi
from tortuga.db.dbManager import DbManager


class GetUsableNodesCli(TortugaCli):
    """
    Get nodes that can be used in a software profile
    """

    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Software Profile Attribute Options')

        self.addOptionGroup(
            softwareProfileAttrGroup,
            _('Software profile must be specified.'))

        self.addOptionToGroup(
            softwareProfileAttrGroup,
            '--software-profile',
            metavar='NAME', required=True,
            dest='softwareProfile',
            help=_('Software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Display list of nodes able to use the specified software profile.
"""))

        with DbManager().session() as session:
            print('\n'.join(
                [node.getName()
                 for node in SoftwareProfileDbApi().getUsableNodes(
                     session, self.getArgs().softwareProfile)]))


def main():
    GetUsableNodesCli().run()
