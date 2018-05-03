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

import sys
import json

from tortuga.network.networkCli import NetworkCli


class GetNetworkListCli(NetworkCli):
    """
    Get list tortuga command line interface.

    """

    def parseArgs(self, usage=None):
        output_attr_group = _('Output formatting options')

        self.addOptionGroup(output_attr_group, None)

        self.addOptionToGroup(
            output_attr_group, '--json',
            action='store_true', default=False,
            help=_('JSON formatted output')
        )

        self.addOptionToGroup(
            output_attr_group, '--xml',
            action='store_true', default=False,
            help=_('XML formatted output')
        )

        super(GetNetworkListCli, self).parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Return list of networks in the system'))

        network_list = self.getNetworkApi().getNetworkList()

        if not network_list:
            sys.exit(1)

        if self.getArgs().xml:
            print(network_list.getXmlRep())
        elif self.getArgs().json:
            print(json.dumps(network_list.getCleanDict(),
                             sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            self._console_output(network_list)

    def _console_output(self, networks):
        for network in networks:
            print('- Network: {0}/{1}'.format(network.getAddress(),
                                              network.getNetmask()))

            print(' ' * 2 + '- Name: {0}'.format(network.getName()))

            print(' ' * 2 + '- Type: {0}'.format(network.getType()))

            print(' ' * 2 + '- DHCP enabled: {0}'.format(
                network.getUsingDhcp()))

            if network.getStartIp():
                print(' ' * 2 + '- Start IP: {0}'.format(network.getStartIp()))

            if network.getGateway():
                print(' ' * 2 + '- Gateway: {0}'.format(network.getGateway()))


def main():
    GetNetworkListCli().run()
