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

import argparse

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.nodeWsApi import NodeWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class ComponentCli(TortugaCli):
    def __init__(self):
        super().__init__()

        self.software_profile_api = None

        self.software_profile_name = None
        self.kit_name = None
        self.kit_version = None
        self.kit_iteration = None
        self.component_name = None

    def parseArgs(self, usage=None):
        excl_option_group = self.getParser().add_mutually_exclusive_group(
            required=True)

        excl_option_group.add_argument(
            '--software-profile', dest='softwareProfileName',
            metavar='NAME',
            help=_('Software profile to act on'))

        excl_option_group.add_argument(
            '-p',
            dest='applyToInstaller', action='store_true',
            default=False,
            help=_('Perform action on Tortuga installer software profile')
        )

        self.addOption('--kit-name', dest='kitName', metavar='NAME',
                       help=_('kit name'))

        self.addOption('--kit-version', dest='kitVersion',
                       metavar='VERSION',
                       help=_('kit version'))

        self.addOption('--kit-iteration', dest='kitIteration',
                       metavar='ITERATION',
                       help=_('kit iteration'))

        self.addOption('--comp-name', dest='compName',
                       metavar='NAME',
                       help=_('component name'))

        self.addOption('--comp-version', dest='compVersion',
                       metavar='VERSION',
                       help=_('component version'))

        self.addOption('--no-sync', dest='sync', action='store_false',
                       default=True,
                       help=argparse.SUPPRESS)

        self.addOption('args', nargs='*')

        super().parseArgs(usage=usage)

        if self.getArgs().args:
            if len(self.getArgs().args) == 1 and \
                    '-' not in self.getArgs().args[0]:
                # The first argument is assumed to be the component name.
                self.component_name = self.getArgs().args[0]

                self.kit_name = self.getArgs().kitName
                self.kit_version = self.getArgs().kitVersion
                self.kit_iteration = self.getArgs().kitIteration
            else:
                # Get given Kit information
                kit_name = None
                if len(self.getArgs().args) >= 1:
                    kit_name = self.getArgs().args[0]

                # get installed kit name/version/iteration using name only
                self.kit_name, self.kit_version, self.kit_iteration = \
                    self.getKitNameVersionIteration(kit_name)

                # Get given Component information
                if len(self.getArgs().args) >= 2:
                    vals = self.getArgs().args[1].rsplit('-', 1)
                    self.component_name = vals[0]

                if not self.component_name:
                    self.usage(_('Missing component name'))
        else:
            # copy args from command-line
            self.kit_name = self.getArgs().kitName
            self.kit_version = self.getArgs().kitVersion
            self.kit_iteration = self.getArgs().getIteration
            self.component_name = self.getArgs().compName

        # Get the given software profile information
        self.software_profile_name = self.__get_software_profile_name()

        self.software_profile_api = self.configureClient(SoftwareProfileWsApi)

    def getKitNameVersionIteration(self, pkgname):
        if pkgname:
            a = pkgname.split('-')

            name = a[0]
            version = None
            iteration = None

            if len(a) == 3:
                version = '-'.join(a[1:-1])
                iteration = a[-1]
            elif len(a) == 2:
                version = a[1]
        else:
            name = self.getArgs().kitName
            version = self.getArgs().kitVersion
            iteration = self.getArgs().kitIteration

        return name, version, iteration

    def __get_software_profile_name(self):
        """
        Returns software profile name based on command-line arguments or None,
        if not provided.
        """

        if self.getArgs().applyToInstaller:
            nodeApi = self.configureClient(NodeWsApi)
            node = nodeApi.getInstallerNode(optionDict={
                'softwareprofile': True,
            })

            return node.getSoftwareProfile().getName()

        return self.getArgs().softwareProfileName
