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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.softwareprofile.softwareProfileFactory \
    import getSoftwareProfileApi
from tortuga.hardwareprofile.hardwareProfileFactory \
    import getHardwareProfileApi
from tortuga.node.nodeApiFactory import getNodeApi


class GetActiveChildrenCli(TortugaCli):
    """
    Get the idle children of a software profile
    """

    def __init__(self):
        TortugaCli.__init__(self)

    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Idle Children Attribute Options')

        self.addOptionGroup(
            softwareProfileAttrGroup,
            _('Software Profile name must be specified.'))

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--software-profile',
            metavar='NAME', required=True,
            dest='softwareProfileName', help=_('software profile name'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Get the list of active nodes associated with a given software profile.
"""))

        softwareProfileName = self.getArgs().softwareProfileName

        swapi = getSoftwareProfileApi(self.getUsername(), self.getPassword())
        hwapi = getHardwareProfileApi(self.getUsername(), self.getPassword())
        napi = getNodeApi(self.getUsername(), self.getPassword())

        nodeList = napi.getNodeList()

        softwareProfile = swapi.getSoftwareProfile(softwareProfileName)

        noKids = True
        for node in nodeList:
            if not node.getIsIdle():
                hwPId = node.getHardwareProfile().getId()

                # Get the hardware profile
                hardwareProfile = hwapi.getHardwareProfileById(hwPId)

                # Get the hypervisorSoftwareProfileId
                parentSoftwareProfileId = \
                    hardwareProfile.getHypervisorSoftwareProfileId()

                if softwareProfile.getId() == parentSoftwareProfileId:
                    noKids = False

                    print('%s' % (node.getName()))

        if noKids:
            print('No active children found for software profile %s' % (
                softwareProfileName))


def main():
    GetActiveChildrenCli().run()
