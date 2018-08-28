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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.nodeWsApi import NodeWsApi


class TransferNodeCli(TortugaCli):
    """
    Transfer node command line interface.
    """

    def parseArgs(self, usage=None):
        excl_group = \
            self.getParser().add_mutually_exclusive_group(required=True)

        excl_group.add_argument(
            '--node', dest='nodespec', metavar='NODESPEC',
            help=_('Name of node(s) to transfer'))

        excl_group.add_argument(
            '--count', '-n', metavar='COUNT',
            help=_('Number of nodes to transfer'), type=int)

        self.addOption(
            '--src-software-profile',
            dest='srcSoftwareProfileName', metavar='NAME',
            help=_('Source software profile'))

        self.addOption(
            '--software-profile', dest='softwareProfileName',
            required=True, metavar='NAME',
            help=_('Destination software profile'))

        self.addOption(
            '--force', dest='force', action='store_true', default=False,
            help=_('Force node transfer regardless of node state'))

        super().parseArgs(usage=usage)

        if self.getArgs().nodespec and \
                self.getArgs().srcSoftwareProfileName:
            self.getParser().error(
                'argument --node: not allowed with argument:'
                ' --src-software-profile'
            )

    def runCommand(self):
        self.parseArgs('''
Transfer nodes from one software profile to
another. This operation may need a reinstall of the node to apply
the new software profile.
''')

        api = NodeWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl(),
            verify=self._verify
        )

        api.transferNodes(
            self.getArgs().softwareProfileName,
            srcSoftwareProfile=self.getArgs().srcSoftwareProfileName,
            count=self.getArgs().count
            if not self.getArgs().nodespec else None,
            bForce=self.getArgs().force,
            nodespec=self.getArgs().nodespec,
        )


def main():
    TransferNodeCli().run()
