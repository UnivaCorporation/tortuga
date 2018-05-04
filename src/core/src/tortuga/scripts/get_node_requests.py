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


import json
import sys
from typing import NoReturn

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.nodeWsApi import NodeWsApi


class GetNodeRequestsCli(TortugaCli):
    def __init__(self):
        super(GetNodeRequestsCli, self).__init__()

        self.node_wsapi = None

    def parseArgs(self, usage=None):
        self.addOption('--request-id', '-r')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        self.node_wsapi = NodeWsApi(username=self.getUsername(),
                                    password=self.getPassword(),
                                    baseurl=self.getUrl())

        if self.getArgs().request_id:
            self._get_node_request(self.getArgs().request_id)

            raise SystemExit(0)

        for nr in self.node_wsapi.getNodeRequests():
            self.__display_node_request(nr)

    def __display_node_request(self, nr): \
            # pylint: disable=no-self-use
        print(nr['addHostSession'], nr['timestamp'], nr['state'], nr['action'])

        if nr['state'] == 'error':
            print('    ' + nr['message'])
        else:
            print()

    def _get_node_request(self, request_id) -> NoReturn:
        node_requests = \
            self.node_wsapi.getNodeRequests(addHostSession=request_id)

        if not node_requests:
            # Check for node
            nodes = self.node_wsapi.getNodeList(addHostSession=request_id)

            if nodes:
                sys.stdout.write(
                    'The following nodes were added successfully by'
                    ' this request:\n%s' % (
                        '\n'.join([node.getName() for node in nodes])) + '\n')
                sys.stdout.flush()

                sys.exit(0)
            else:
                sys.stderr.write(
                    'Error: node request [{0}] does not exist or'
                    ' is invalid.\n'.format(request_id))

            sys.exit(1)

        node_request = node_requests[0]

        request = json.loads(node_request['request'])

        if node_request['state'] == 'error':
            msg = ('Error attempting to add {} node(s) to hardware'
                    ' profile [{}]'.format(
                        request['count'], request['hardwareProfile']))

            print(msg)

            print('Reported:', node_request['message'])
        else:
            self.__display_node_request(node_request)


def main():
    GetNodeRequestsCli().run()
