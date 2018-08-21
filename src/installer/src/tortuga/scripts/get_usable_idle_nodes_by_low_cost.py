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
from tortuga.db.dbManager import DbManager
from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.db.softwareUsesHardwareDbApi import SoftwareUsesHardwareDbApi
from tortuga.kit.loader import load_kits
from tortuga.node.nodeApi import NodeApi


class GetUsableIdleNodesByLowCostCli(TortugaCli):
    """
    Get nodes that can be used in a software profile
    """

    def __init__(self):
        TortugaCli.__init__(self)

    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Software Profile Attribute Options')
        self.addOptionGroup(
            softwareProfileAttrGroup,
            _('Software profile name must be specified.'))
        self.addOptionToGroup(softwareProfileAttrGroup,
                              '--software-profile', dest='softwareProfile',
                              metavar='NAME', required=True,
                              help=_('software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Display list of nodes able to use the specified software profile,
ordered by cost.
"""))
        softwareProfileName = self.getArgs().softwareProfile

        nodeApi = NodeApi()
        softwareUsesHardwareDbApi = SoftwareUsesHardwareDbApi()
        hardwareProfileDbApi = HardwareProfileDbApi()

        load_kits()

        with DbManager().session() as session:
            hwPList = hardwareProfileDbApi.getHardwareProfileList(session)

            hardwareProfileIdList = softwareUsesHardwareDbApi.\
                getAllowedHardwareProfilesBySoftwareProfileName(
                    session, softwareProfileName)

            nodeList = nodeApi.getNodeList(session)
            usableNodes = []
            for node in nodeList:
                if (node.getHardwareProfile().getId() in hardwareProfileIdList) \
                        and node.getIsIdle():
                    usableNodes.append(node)

            costNameList = []
            for node in usableNodes:
                nodeHwP = node.getHardwareProfile().getId()
                for hwP in hwPList:
                    if hwP.getId() == nodeHwP:
                        costNameList.append([int(hwP.getCost()), node.getName()])
                        break

            costNameList.sort()

            for node in costNameList:
                print('%s' % (node[1]))


def main():
    GetUsableIdleNodesByLowCostCli().run()
