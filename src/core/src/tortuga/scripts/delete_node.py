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

import itertools
import optparse
import sys

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.nodeWsApi import NodeWsApi


class DeleteNodeCli(TortugaCli):
    """
    Delete node command line interface.
    """

    def __init__(self):
        super(DeleteNodeCli, self).__init__(validArgCount=100)

        self.addOption('--node', dest='nodeList', default=[],
                       help=_('Name or list of node(s) to delete'))

        # This is a deprecated option. Accept the '--force' argument, but
        # don't do anything with it.
        self.addOption('--force', action='store_true',
                       default=False,
                       help=optparse.SUPPRESS_HELP)



    def runCommand(self):

        self.parseArgs('''
    delete-node --node=NAME
    delete-node --node=NAME[,NODE...]
    delete-node NAME [NODE]...

Description:
    The delete-node tool removes node(s) from the system.
''')

        if not self.getOptions().nodeList and not self.getArgs():
            self.getParser().error(_('Missing --node option'))

        node_api = NodeWsApi(username=self.getUsername(),
                             password=self.getPassword(),
                             baseurl=self.getUrl()
        )

        if self.getOptions().nodeList and \
                self.getOptions().nodeList[0] == '-':
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
            nodes = self.getOptions().nodeList

            if self.getArgs():
                nodes += ',' + ','.join(self.getArgs())

            node_api.deleteNode(nodes)


def main():
    DeleteNodeCli().run()
