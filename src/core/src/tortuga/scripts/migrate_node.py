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


class MigrateNodeCli(TortugaCli):
    def __init__(self):
        super().__init__()

        option_group_name = _('Migrate Node Options')

        self.addOptionGroup(option_group_name, '')

        self.addOptionToGroup(
            option_group_name, '--node',
            dest='nodeName',
            help=_('Name of node to migrate'))

        self.addOptionToGroup(
            option_group_name, '--destination',
            dest='destinationString',
            help=_('List of nodes which can be the destination'))

        self.addOptionToGroup(
            option_group_name, '--with-shutdown',
            dest='liveMigrate',
            action='store_false',
            default=True,
            help=_('Migrate by shutting down/restarting node'))

    def runCommand(self):
        self.parseArgs(_("""
    migrate-node --node=NODENAME --destination=PARENT[,PARENT] [--with-shutdown]

Description:
    The migrate-node tool migrates a node from one parent
    node to another.

    NOTE: Both the resource adapter and the storage adapter for
    the given node must support this operation.
"""))

        if not self.getArgs().nodeName:
            raise InvalidCliRequest(_('Node name must be specified'))

        if not self.getArgs().destinationString:
            raise InvalidCliRequest(_('Destination must be specified'))

        node_name = self.getArgs().nodeName
        destination_string = self.getArgs().destinationString

        node_api = NodeWsApi(username=self.getUsername(),
                             password=self.getPassword(),
                             baseurl=self.getUrl())

        try:
            # Turn user input into a list
            destination_list = [
                node for node in destination_string.split(',')]

            node_api.migrateNode(
                node_name, destination_list, self.getArgs().liveMigrate)

            print(_('Migrated node: {}').format(node_name))

        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't migrate node [{0}] - {1}").format(node_name, msg))


def main():
    MigrateNodeCli().run()
