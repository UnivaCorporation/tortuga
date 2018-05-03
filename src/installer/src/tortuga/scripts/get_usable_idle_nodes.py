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
from tortuga.node.nodeApiFactory import getNodeApi
from tortuga.db.softwareUsesHardwareDbApi import SoftwareUsesHardwareDbApi


class GetUsableIdleNodesCli(TortugaCli):
    """
    Get nodes that can be used in a software profile
    """

    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Software Profile Attribute Options')

        self.addOptionGroup(
            softwareProfileAttrGroup,
            _('Software profile must be specified.'))

        self.addOptionToGroup(softwareProfileAttrGroup,
                              '--software-profile',
                              dest='softwareProfile',
                              metavar='NAME', required=True,
                              help=_('software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Display list of nodes that are able to use the specified software profile.
"""))
        softwareProfileName = self.getArgs().softwareProfile

        nodeApi = getNodeApi(self.getUsername(), self.getPassword())

        softwareUsesHardwareDbApi = SoftwareUsesHardwareDbApi()

        # YAY for super long API names
        hardwareProfileIdList = \
            softwareUsesHardwareDbApi.\
            getAllowedHardwareProfilesBySoftwareProfileName(
                softwareProfileName)

        nodeList = nodeApi.getNodeList()

        for node in nodeList:
            if node.getHardwareProfile().getId() in \
               hardwareProfileIdList and node.getIsIdle():
                print('%s' % node)


def main():
    GetUsableIdleNodesCli().run()
