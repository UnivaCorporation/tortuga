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
        self.getParser().add_argument(
            '--node', dest='nodeList',
            help=argparse.SUPPRESS)

        self.getParser().add_argument(
            '--name', dest='nodeList', metavar='NODESPEC',
            help=_('Node(s) to be deleted'))

        self.getParser().add_argument(
            'nodes', metavar='NAME',
            help='Node(s) to be deleted',
            nargs='*',
        )

        self.addOption('--force', action='store_true',
                       default=False,
                       help=_('Allow deletion of nodes from soft locked'
                              ' software profile.'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        node_api = self.configureClient(NodeWsApi)

        if (self.getArgs().nodeList and self.getArgs().nodeList[0] == '-') or \
                (self.getArgs().nodes and self.getArgs().nodes[0] == '-'):
            # Perform bulk deletes, 100 nodes at a time

            nodes = []
            for count, line in zip(itertools.count(1), sys.stdin.readlines()):
                nodes.append(line.rstrip())

                if count % 100 == 0:
                    node_api.deleteNode(','.join(nodes), force=self.getArgs().force)

                    nodes = []

            if nodes:
                node_api.deleteNode(
                    ','.join(nodes), force=self.getArgs().force)
        else:
            nodes = []

            for nodespec in self.getArgs().nodes:
                nodes.extend(nodespec.split(','))

            if self.getArgs().nodeList:
                nodes.append(self.getArgs().nodeList)

            node_api.deleteNode(','.join(nodes), force=self.getArgs().force)

def main():
    DeleteNodeCli().run()
