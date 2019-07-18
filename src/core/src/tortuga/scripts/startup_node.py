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


class StartupNodeCli(TortugaCli):
    def parseArgs(self, usage=None):
        optionGroupName = _('Startup Node Options')

        self.addOptionGroup(optionGroupName, '')

        self.addOptionToGroup(
            optionGroupName, '--node', required=True,
            dest='nodeName',
            help=_('Name of node to start'))

        self.addOptionToGroup(
            optionGroupName, '--destination',
            dest='destinationString',
            help=_('List of nodes which can be the destination'))

        self.addOptionToGroup(optionGroupName, '--boot-method',
                              dest='bootMethod', default='n',
                              help=_('Boot method'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        # Turn user input into a list
        destinationList = [
            node.strip()
            for node in self.getArgs().destinationString.split(',')
        ] if self.getArgs().destinationString else []

        api = self.configureClient(NodeWsApi)
        try:
            api.startupNode(self.getArgs().nodeName, destinationList,
                            self.getArgs().bootMethod)

        except Exception as msg:
            raise InvalidCliRequest(
                _("Unable to start node(s) - %s") % (msg))


def main():
    StartupNodeCli().run()
