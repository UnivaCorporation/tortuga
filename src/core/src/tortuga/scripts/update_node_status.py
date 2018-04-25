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

import socket

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi import nodeWsApi


class UpdateNodeStatusCli(TortugaCli):
    """
    update-node-status CLI
    """

    def parseArgs(self, usage=None):
        nodeName = socket.getfqdn()

        self.addOption("--node", dest='nodeName', default=nodeName,
                       help='Name of the node for which status is being'
                            ' updated')

        self.addOption('--status', dest='status', default='Installed',
                       help='Updated node status')

        self.addOption('--boot-from', dest='bootFrom', default=1,
                       help='Updated boot-from flag')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        # Always go over the web service for this call.
        nodeWsApi.NodeWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl()).updateNodeStatus(
                self.getArgs().nodeName,
                self.getArgs().status,
                self.getArgs().bootFrom)


def main():
    UpdateNodeStatusCli().run()
