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
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.wsapi import nodeWsApi


class ActivateNodeCli(TortugaCli):
    """
    Activate node command line interface.

    """

    def parseArgs(self, usage=None):
        self.addOption('--node',
                       dest='nodeName',
                       help=_('Name of node to activate'))
        self.addOption('--software-profile',
                       dest='softwareProfileName',
                       help=_('Destination software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs('''
Transfers given idle node to the given active software profile.
''')

        software_profile_name = self.getArgs().softwareProfileName

        if not self.getArgs().nodeName:
            self.usage('Missing --node option')

        api = nodeWsApi.NodeWsApi(username=self.getUsername(),
                                  password=self.getUsername(),
                                  baseurl=self.getUrl())

        try:
            result = api.activateNode(
                self.getArgs().nodeName, software_profile_name)

            if result['NodeAlreadyActive']:
                msg = _('The following node(s) are already activated:')

                print(msg)

                print('\n'.join(result['NodeAlreadyActive']))

            if result['SoftwareProfileNotFound']:
                msg = _('Software profile not specified for following'
                        ' node(s):')

                print(msg)

                print('\n'.join(result['SoftwareProfileNotFound']))

            if result['InvalidArgument']:
                msg = _('The software profile [%s] for the following'
                        ' node(s) is already idle:')

                print(msg)

                print('\n'.join(result['InvalidArgument']))

            if result['NodeSoftwareProfileLocked']:
                msg = _('The following node(s) cannot be activated while'
                        'locked:')

                print(msg)

                print('\n'.join(result['NodeSoftwareProfileLocked']))

            for nodeName, hardwareProfileName, software_profile_name in \
                    result['ProfileMappingNotAllowed']:
                print(_('Node [{0}] belongs to hardware profile [{1}], which'
                        ' is not allowed to use software profile'
                        ' [{2}]').format(nodeName, hardwareProfileName,
                                         software_profile_name))
        except TortugaException as ex:
            print(_("Error: Can't activate node(s) - {}".format(ex)))

            raise SystemExit(255)


def main():
    ActivateNodeCli().run()
