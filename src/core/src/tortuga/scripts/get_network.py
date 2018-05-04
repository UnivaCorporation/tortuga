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

from tortuga.network.networkCli import NetworkCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest


class GetNetworkCli(NetworkCli):
    """
    Get tortuga command line interface.

    """
    def __init__(self):
        super().__init__()

    def parseArgs(self, usage=None):

        # The get command can take only the network option
        self.addOption('--network', dest='network',
                       help=_('Network identifier ("address/netmask")'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Get details of a specific network.'))

        # Parse --network parameter if it exists
        networkAddress, networkMask = self.parseNetworkParameter(
            self.getArgs().network)

        # If we don't have a network and a netmask its an error
        if networkAddress is not None and networkMask is not None:
            network = self.getNetworkApi().getNetwork(
                networkAddress, networkMask)
        else:
            raise InvalidCliRequest(
                _('The --network parameter must be specified.'))

        # TODO: do not output XML
        print(network.getXmlRep())


def main():
    GetNetworkCli().run()
