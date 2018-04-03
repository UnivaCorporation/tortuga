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

from tortuga.puppet import Puppet
from tortuga.kit.kitCli import KitCli
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class DisableComponent(KitCli):
    def __init__(self):
        super().__init__(validArgCount=2)

        self.addOption('--software-profile', dest='softwareProfileName',
                       help=_('Software profile to disable component on'))

        self.addOption(
            '-p', '',
            dest='applyToInstaller', action='store_true',
            default=False,
            help=_('Shortcut for \'--software-profile Installer\'')
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

    def runCommand(self):

        self.parseArgs('''
     disable-component --software-profile=SWPROFILENAME --kit-name=KITNAME
       --kit-version=KITVER   --kit-iteration=KITITER   --comp-name=COMPNAME
       --comp-version=COMPVER

    disable-component  --software-profile=SWPROFILENAME
         KITNAME-KITVER-KITITER COMPNAME-COMPVER

    Disable component on software profile of installer:

    disable-component -p --kit-name=KITNAME --kit-version=KITVER
       --kit-iteration=KITITER --comp-name=COMPNAME --comp-version=COMPVER

    disable-component -p KITNAME-KITVER-KITITER COMPNAME-COMPVER

Description:
    The disable-component tool is used to remove an association between a
    component  and  a  software profile.  After running disable-component
    and puppet agent, the components software should be removed  from the
    machines belonging to the specified software profile.

Examples:
    These two examples are equivalent:

    disable-component --software-profile DefaultCompute ganglia-3.0.7-1 \
component-ganglia-gmond-3.0.7

    disable-component --software-profile DefaultCompute --kit-name ganglia \
--kit-version 3.0.7 --kit-iteration 1 --comp-name component-ganglia-gmond \
--comp-version 3.0.7
''')

        if self.getNArgs() == 1 and '-' not in self.getArg(0):
            # The first argument is assumed to be the component name.
            compname = self.getArg(0)
            kit_name = None
            kit_version = None
            kit_iteration = None
        else:
            # Get given Kit information
            pkgname = None
            if self.getNArgs() >= 1:
                pkgname = self.getArg(0)

            kit_name, kit_version, kit_iteration = \
                self.getKitNameVersionIteration(pkgname)

            # Get given Component information

            compname = None
            if self.getNArgs() >= 2:
                compspec = self.getArg(1)

                if '-' in compspec:
                    compname, _ = compspec.rsplit('-', 1)
                else:
                    compname = compspec

        # Get the given softwareProfile information

        if self._options.applyToInstaller:
            from tortuga.node import nodeApiFactory
            node_api = nodeApiFactory.getNodeApi()

            node = node_api.getInstallerNode(optionDict={
                'softwareprofile': True,
            })

            software_profile_name = node.getSoftwareProfile().getName()
        else:
            software_profile_name = self._options.softwareProfileName

            if not software_profile_name:
                self.usage(_('Missing --software-profile option'))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.disableComponent(software_profile_name, kit_name, kit_version,
                             kit_iteration, compname)

        if self.getOptions().sync:
            Puppet().agent()


def main():
    DisableComponent().run()
