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

import platform
import subprocess
import sys

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.dbManager import DbManager
from tortuga.kit.kitApiFactory import getKitApi


class InstallKitCli(TortugaCli):
    """
    Install kit command line interface.
    """

    def parseArgs(self, usage=None):
        kitPkgGroup = _('Kit Package Option')
        self.addOptionGroup(
            kitPkgGroup, _('If kit package URL is provided, kit'
                           ' /name/version/iteration are not used.'))

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

        # restart tortugawsd and celery after installing new kit
        cmd = None
        try:
            if platform.dist()[1].startswith('7'):
                cmd = 'systemctl restart tortugawsd celery'
        except ValueError:
            pass

        if not cmd:
            cmd = 'service tortugawsd restart && service celery restart'

        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        retval = p.wait()
        if retval != 0:
            print(
                'Error restarting services: rc=[{}]'.format(retval),
                file=sys.stderr
            )

            sys.exit(1)

    def installKitHelper(self, api, key=None, accept_eula=False):
        dbm = DbManager()

        args = self.getArgs()

        if args.package_uri:
            return api.installKitPackage(dbm, self.getArgs().package_uri, key)

        return api.installKit(dbm, args.name, args.version, args.iteration, key)


def main():
    InstallKitCli().run()
