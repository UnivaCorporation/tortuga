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
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.nodeWsApi import NodeWsApi


class RevertNodeToCheckpointCli(TortugaCli):
    def parseArgs(self, usage=None):
        optionGroupName = _('Checkpoint Node Options')
        self.addOptionGroup(optionGroupName, '')
        self.addOptionToGroup(optionGroupName, '--node',
                              dest='nodeName',
                              required=True,
                              metavar='NAME',
                              help=_('Name of node to revert'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Revert given node back to the last checkpoint.
"""))

        nodeName = self.getArgs().nodeName

        try:
            nodeApi = NodeWsApi(username=self.getUsername(),
                                password=self.getPassword(),
                                baseurl=self.getUrl())
        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't revert node [{0}] - {1}").format(nodeName, msg))

        try:
            nodeApi.revertNodeToCheckpoint(nodeName)
        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't revert node [{0}] - {1}").format(nodeName, msg))


def main():
    RevertNodeToCheckpointCli().run()
