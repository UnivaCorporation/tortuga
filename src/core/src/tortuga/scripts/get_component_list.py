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
import gettext

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.helper.osHelper import getOsInfo
from tortuga.wsapi.kitWsApi import KitWsApi
from tortuga.wsapi.nodeWsApi import NodeWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi

_ = gettext.gettext


def displayComponent(c, kit):
    # Depends on the __repr__ of Component and Kit objects
    print('%s %s' % (kit, c))


class GetComponentList(TortugaCli):
    def parseArgs(self, usage=None):
        optGroup = 'Options'

        group = self.addOptionGroup(optGroup, '')

        excl_option_group = group.add_mutually_exclusive_group()

        excl_option_group.add_argument(
            '--software-profile',
            dest='softwareprofile',
            help=_('Display list of components enabled in software profile.')
        )

        excl_option_group.add_argument(
            '-p',
            dest='applyToInstaller',
            action='store_true',
            default=False,
            help=_('Display components enabled on installer only')
        )

        excl_option_group.add_argument(
            '--os',
            dest='os',
            metavar='NAME-VERSION-ARCH',
            help=_('Display components suitable for specified OS only')
        )

        super().parseArgs(usage=usage)

    def __get_software_profile(self):
        # Determine software profile name based on command-line option(s)

        if self.getArgs().applyToInstaller:
            # Get software profile name from installer node
            node = NodeWsApi(
                username=self.getUsername(),
                password=self.getPassword(),
                baseurl=self.getUrl()
            ).getInstallerNode(
                optionDict={
                    'softwareprofile': True,
                }
            )

            return node.getSoftwareProfile().getName()

        return self.getArgs().softwareprofile

    def runCommand(self):
        self.parseArgs(_("""
Display list of components available for software profiles in the system.
"""))

        softwareProfileName = self.__get_software_profile()

        if softwareProfileName:
            # Display all components enabled for software profile

            for c in SoftwareProfileWsApi(username=self.getUsername(),
                                          password=self.getPassword(),
                                          baseurl=self.getUrl()
                                          ).getEnabledComponentList(
                    softwareProfileName):
                displayComponent(c, c.getKit())

            return

        if self.getArgs().os:
            try:
                name, version, arch = self.getArgs().os.split('-', 3)
            except ValueError:
                self.getParser().error(
                    'Malformed argument to --os. Must be in form of'
                    ' NAME-VERSION-ARCH')

            osinfo = getOsInfo(name, version, arch)
        else:
            osinfo = None

        # Display all components
        for kit in KitWsApi(
                username=self.getUsername(),
                password=self.getPassword(),
                baseurl=self.getUrl()).getKitList():
            for c in kit.getComponentList():
                if osinfo and osinfo not in c.getOsInfoList() and \
                        osinfo.getOsFamilyInfo() not in c.getOsFamilyInfoList():
                    # Exclude those components that cannot be enabled on the
                    # specified operating system.
                    continue

                displayComponent(c, kit)


def main():
    GetComponentList().run()
