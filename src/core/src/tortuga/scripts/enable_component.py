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

from tortuga.kit.kitCli import KitCli
from tortuga.puppet import Puppet
from tortuga.wsapi.nodeWsApi import NodeWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class ComponentCli(KitCli):
    def __init__(self):
        super().__init__()

        self.softwareProfileName = None
        self.kitName = None
        self.kitVersion = None
        self.kitIteration = None
        self.compname = None

    def parseArgs(self, usage=None):
        excl_option_group = self.getParser().add_mutually_exclusive_group()

        excl_option_group.add_argument(
            '--software-profile', dest='softwareProfileName',
            help=_('Software profile to act on'))

        excl_option_group.add_argument(
            '-p',
            dest='applyToInstaller', action='store_true',
            default=False,
            help=_('Perform action on Tortuga installer software profile')
        )

        self.addOption('--kit-name', dest='kitName',
                       help=_('kit name'))
        self.addOption('--kit-version', dest='kitVersion',
                       help=_('kit version'))
        self.addOption('--kit-iteration', dest='kitIteration',
                       help=_('kit iteration'))
        self.addOption('--comp-name', dest='compName',
                       help=_('component name'))
        self.addOption('--comp-version', dest='compVersion',
                       help=_('component version'))
        self.addOption('--no-sync', dest='sync', action='store_false',
                       default=True, help=_('component version'))

        self.addOption('args', nargs='*')

        super().parseArgs(usage=usage)

        if self.getArgs().args:
            if len(self.getArgs().args) == 1 and '-' not in self.getArgs().args[0]:
                # The first argument is assumed to be the component name.
                compname = self.getArgs().args[0]

                kitName = self.getArgs().kitName
                kitVersion = self.getArgs().kitVersion
                kitIteration = self.getArgs().kitIteration
            else:
                # Get given Kit information
                pkgname = None
                if len(self.getArgs().args) >= 1:
                    pkgname = self.getArgs().args[0]

                kitName, kitVersion, kitIteration = \
                    self.getKitNameVersionIteration(pkgname)

                # Get given Component information
                compname = None
                if len(self.getArgs().args) >= 2:
                    vals = self.getArgs().args[1].rsplit('-', 1)
                    compname = vals[0]

                if not compname:
                    self.usage(_('Missing component name'))

        # Get the given software profile information
        softwareProfileName = self.__get_software_profile_name()

        if not softwareProfileName:
            self.usage(_('Missing --software-profile option'))

        self.softwareProfileName = softwareProfileName
        self.kitName = kitName
        self.kitVersion = kitVersion
        self.kitIteration = kitIteration
        self.compname = compname

    def __get_software_profile_name(self):
        """
        Returns software profile name based on command-line arguments or None,
        if not provided.
        """

        if self.getArgs().applyToInstaller:
            nodeApi = NodeWsApi(username=self.getUsername(),
                                password=self.getPassword(),
                                baseurl=self.getUrl())

            node = nodeApi.getInstallerNode(optionDict={
                'softwareprofile': True,
            })

            return node.getSoftwareProfile().getName()

        return self.getArgs().softwareProfileName


class EnableComponent(ComponentCli):
    def runCommand(self):
        self.parseArgs('''
Enable component on software profile.
''')

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.enableComponent(
            self.softwareProfileName, self.kitName, self.kitVersion, self.kitIteration,
            self.compname)

        if self.getArgs().sync:
            Puppet().agent()


def main():
    EnableComponent().run()
