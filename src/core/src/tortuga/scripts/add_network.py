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

from tortuga.objects.network import Network
from tortuga.network.networkCli import NetworkCli


class AddNetworkCli(NetworkCli):
    """
    Add tortuga command line interface.

    """
    def __init__(self):
        super(AddNetworkCli, self).__init__()

        # Now add in the default options
        self.setupDefaultOptions()

    def runCommand(self):
        self.parseArgs(_("""
Registers a network within Tortuga. This network can then be associated with
hardware profile(s) to allow Tortuga to manage cluster node networking
configuration.
"""))

        network = self.get_network_from_cmdline(retrieve_network=False)

        if network is None:
            network = Network()

        # Apply command line parameters
        self.updateNetwork(network)

        # Check for required parameters
        self.validateNetwork(network)

        # Save the updated network
        self.getNetworkApi().addNetwork(network)


def main():
    AddNetworkCli().run()
