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
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.nodeWsApi import NodeWsApi


class IdleNodeCli(TortugaCli):
    """
    Idle node command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption('--node', dest='nodeName', required=True,
                       help=_('Name of node to idle'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs('''
Marks active node idle which will cause varying
actions based on the resource adapter associated with the given node.
''')

        # The "--node nodeName" option was implemented first
        # and we maintain backwards compatability for it.
        # The "nodeName..." arguments were added later.

        node_api = NodeWsApi(username=self.getUsername(),
                             password=self.getPassword(),
                             baseurl=self.getUrl(),
                             verify=self._verify)

        try:
            results = node_api.idleNode(self.getArgs().nodeName)

            if results['NodeAlreadyIdle']:
                print(
                    _('The following node(s) are already in idle state:')
                )
                print('\n'.join(results['NodeAlreadyIdle']))

            if results['NodeSoftwareProfileLocked']:
                print(
                    _('The following node(s) are locked and cannot be idled:')
                )
                print('\n'.join(results['NodeSoftwareProfileLocked']))

        except Exception as msg:
            raise InvalidCliRequest(_("Can't idle node(s): {}").format(msg))


def main():
    IdleNodeCli().run()
