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
from tortuga.wsapi.softwareProfileWsApi \
    import SoftwareProfileWsApi
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest


class GetNodesWithComponentCli(TortugaCli):
    """
    Get list of nodes with a specific component enabled
    """

    def parseArgs(self, usage=None):
        nodeProfileAttrGroup = _('Node Attribute Options')

        self.addOptionGroup(
            nodeProfileAttrGroup,
            _('Options for controlling node result set'))

        self.addOptionToGroup(
            nodeProfileAttrGroup, '--state', dest='state',
            help=_('Return nodes only of the csv list of states'))

        self.addOptionToGroup(nodeProfileAttrGroup, '--count', dest='count',
                              type=int,
                              help=_('Max number of Nodes to return'))

        componentProfileAttrGroup = _('Component Profile Attribute Options')
        self.addOptionGroup(
            componentProfileAttrGroup,
            _('All component items must be specified'))

        self.addOptionToGroup(
            componentProfileAttrGroup, '--kit-name', dest='kitName',
            metavar='NAME', required=True,
            help=_('kit name'))

        self.addOptionToGroup(
            componentProfileAttrGroup, '--kit-version', dest='kitVersion',
            metavar='VERSION', required=True,
            help=_('kit version'))

        self.addOptionToGroup(
            componentProfileAttrGroup, '--kit-iteration',
            metavar='ITERATION', required=True,
            dest='kitIteration',
            help=_('kit iteration name'))

        self.addOptionToGroup(
            componentProfileAttrGroup, '--component-name',
            metavar='NAME', required=True,
            dest='componentName', help=_('component name'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Returns the list of nodes that have the given component enabled. The
result set can be filtered by state and count.
"""))

        state = self.getArgs().state

        if state:
            stateList = state.split(',')

        if self.getArgs().count is not None:
            numNodes = int(self.getArgs().count)
            if numNodes == 0:
                return
        else:
            numNodes = -1

        api = self.configureClient(SoftwareProfileWsApi)

        optionDict = {}
        optionDict['nodes'] = True

        for sp in api.getSoftwareProfileList():
            comps = api.getEnabledComponentList(sp.getName())
            for comp in comps:
                if comp.getName() == self.getArgs().componentName and \
                   comp.getKit().getName() == self.getArgs().kitName and \
                   comp.getKit().getVersion() == \
                   self.getArgs().kitVersion and \
                   comp.getKit().getIteration() == \
                   self.getArgs().kitIteration:
                    softwareProfile = api.getSoftwareProfile(
                        sp.getName(), optionDict)

                    for node in softwareProfile.getNodes():
                        if state is None or node.getState() in stateList:
                            print(node.getName())

                            numNodes = numNodes - 1

                            if numNodes == 0:
                                return


def main():
    GetNodesWithComponentCli().run()
