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

from tortuga.kit.kitCli import KitCli
from tortuga.kit.kitApiFactory import getKitApi


class InstallKitCli(KitCli):
    """
    Install kit command line interface.
    """

    def parseArgs(self, usage=None):
        kitPkgGroup = _('Kit Package Option')
        self.addOptionGroup(
            kitPkgGroup, _('If kit package URL is provided, kit'
                           ' /name/version/iteration are not used.'))

        # self.addOptionToGroup(
        #     kitPkgGroup, '--package', dest='packageUrl',
        #     help=_('kit package URL'))

        self.addOptionToGroup(
            kitPkgGroup, 'package_uri',
            help=_('kit package URI (can be a file name or fully-qualified URL)'),
        )

        self.addOptionToGroup(
            kitPkgGroup, '--i-accept-the-eula', dest='acceptEula',
            action="store_true", default=False,
            help=_('Accept the EULA for this kit.'))

        kitAttrGroup = _('Kit Attribute Options')

        self.addOptionGroup(
            kitAttrGroup, _('If kit package URL is not provided, kit'
                            ' name/version must be specified.'))

        self.addOptionToGroup(
            kitAttrGroup, '--name', dest='name', help=_('kit name'))

        self.addOptionToGroup(
            kitAttrGroup, '--version', dest='version', help=_('kit version'))

        self.addOptionToGroup(
            kitAttrGroup, '--iteration', dest='iteration', default=None,
            help=_('kit iteration'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Adds new application kit to Tortuga'))

        api = getKitApi(self.getUsername(), self.getPassword())

        self.installKitHelper(api, accept_eula=self.getArgs().acceptEula)

    def installKitHelper(self, api, key=None, accept_eula=False): \
            # pylint: disable=unused-argument
        if self.getArgs().package_uri:
            return api.installKitPackage(self.getArgs().package_uri, key)

        name, version, iteration = self.get_name_version_iteration()

        return api.installKit(name, version, iteration, key)


def main():
    InstallKitCli().run()
