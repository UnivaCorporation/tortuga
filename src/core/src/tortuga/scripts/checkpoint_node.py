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


class CheckpointNodeCli(TortugaCli):
    def __init__(self):
        super().__init__()
        option_group_name = _('Checkpoint Node Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--node',
                              metavar='NAME',
                              dest='nodeName',
                              help=_('Name of node to checkpoint'))

    def runCommand(self):
        self.parseArgs(_("""
    checkpoint-node --node=NODENAME

Description:
    The checkpoint-node tool takes a checkpoint of the given node
    which can then be used to revert the node back to should
    the need arise.

    NOTE: Both the node adapter and the storage adapter for
    the given node must support this operation.
"""))

        if not self.getOptions().nodeName:
            raise InvalidCliRequest(_('Node name must be specified'))

        node_name = self.getOptions().nodeName

        try:
            api = NodeWsApi(username=self.getUsername(),
                            password=self.getPassword(),
                            baseurl=self.getUrl())
            api.checkpointNode(node_name)
            print(_('Checkpointed node [%s]') % (node_name))
        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't checkpoint node [{0}] - {1}").format(
                    node_name, msg))


def main():
    CheckpointNodeCli().run()
