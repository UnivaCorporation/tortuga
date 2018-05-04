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

import argparse
import itertools
import sys

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.nodeWsApi import NodeWsApi


class DeleteNodeCli(TortugaCli):
    """
    Delete node command line interface.
    """

    def parseArgs(self, usage=None):
        excl_group = \
            self.getParser().add_mutually_exclusive_group(required=True)

        excl_group.add_argument(
            '--node', dest='nodeList',
            help=argparse.SUPPRESS)

        excl_group.add_argument(
            '--name', dest='nodeList',
            help=_('Name or list of node(s) to delete'))

        # This is a deprecated option. Accept the '--force' argument, but
        # don't do anything with it.
        self.addOption('--force', action='store_true',
                       default=False,
                       help=argparse.SUPPRESS)

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        node_api = NodeWsApi(username=self.getUsername(),
                             password=self.getPassword(),
                             baseurl=self.getUrl()
        )

        if self.getArgs().nodeList[0] == '-':
            # Perform bulk deletes, 100 nodes at a time

            nodes = []
            for count, line in zip(
                    itertools.count(1), sys.stdin.readlines()):
                nodes.append(line.rstrip())

                if count % 100 == 0:
                    node_api.deleteNode(','.join(nodes))

                    nodes = []

            node_api.deleteNode(','.join(nodes))
        else:
            node_api.deleteNode(self.getArgs().nodeList)


def main():
    DeleteNodeCli().run()
