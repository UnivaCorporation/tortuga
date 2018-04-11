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
from typing import Any, Optional, Union, Dict, List
from tortuga.wsapi.nodeWsApi import NodeWsApi
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.cli.utils import FilterTagsAction


class GetNodeStatus(TortugaCli): \
        # pylint: disable=too-few-public-methods
    def __init__(self):
        super(GetNodeStatus, self).__init__()

        self.__active_map: Dict[bool, str] = {
            False: 'Active',
            True: 'Inactive'
        }

        self.__boot_map: Dict[int, str] = {
            0: 'Disk',
            1: 'Network'
        }

    def parseArgs(self, usage=None):
        self.addOption(
            '-n', '--node',
            dest='nodeName',
            help=_('Output the status of the given node.'))

        self.addOption(
            '--by-hwprofile',
            dest='bByHardwareProfile',
            action='store_true',
            default=False,
            help=_('Display node list by hardware profile'
                   ' (default is by software profile)'))

        active_idle_excl_group = self.getParser().add_mutually_exclusive_group()

        active_idle_excl_group.add_argument(
            '--active',
            dest='bActiveNodesOnly',
            action='store_true',
            help=_('Display only active nodes'))

        active_idle_excl_group.add_argument(
            '--idle',
            dest='bIdleNodesOnly',
            action='store_true',
            help=_('Display only idle nodes'))

        installed_not_installed_excl_group = \
            self.getParser().add_mutually_exclusive_group()

        installed_not_installed_excl_group.add_argument(
            '--installed',
            dest='bInstalled',
            action='store_true',
            help=_('Display only nodes that are in \'Installed\' state')
        )

        installed_not_installed_excl_group.add_argument(
            '--not-installed',
            dest='bNotInstalled',
            action='store_true',
            help=_('Display only nodes that are not in \'Installed\' state')
        )

        self.addOption(
            '--state',
            help=_('Filter nodes in specified state')
        )

        self.addOption(
            '--software-profile',
            dest='softwareProfile',
            help=_('Display only nodes in specified software profile')
        )

        self.addOption(
            '--hardware-profile',
            dest='hardwareProfile',
            help=_('Display only nodes in specified hardware profile')
        )

        self.addOption(
            '-s', '--short',
            dest='bShortOutput',
            action='store_true',
            help=_('Display short form output'),
        )

        self.addOption(
            '-l', '--list',
            dest='bListOutput',
            action='store_true',
            help=_('Display host names one per line'),
        )

        self.addOption(
            '--tag',
            action=FilterTagsAction,
            dest='tags',
            help=_('Filter results by specified tag(s) (comma-separated)'),
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        options = self.getArgs()

        if options.state and (options.bNotInstalled or options.bInstalled):
            raise InvalidCliRequest(
                '--state and --installed/--not-installed arguments are'
                ' mutually exclusive'
            )

        api = NodeWsApi(username=self.getUsername(),
                        password=self.getPassword(),
                        baseurl=self.getUrl())

        nodes: List[Dict[str, Any]] = [
            dict(x)
            for x in api.getNodeList(nodespec=options.nodeName,
                                     tags=options.tags)]

        if not nodes:
            if options.nodeName:
                print('No nodes matching nodespec [{}]\n'.format(
                    options.nodeName))

            sys.exit(1)

        if options.bActiveNodesOnly:
            nodes = self.__filter_nodes(nodes, 'isIdle', False)

        if options.bIdleNodesOnly:
            nodes = self.__filter_nodes(nodes, 'isIdle', True)

        if options.bInstalled:
            nodes = self.__filter_nodes(nodes, 'state', 'Installed')

        if options.bNotInstalled:
            nodes = self.__filter_nodes(nodes, 'state', 'Installed', True)

        if options.state:
            nodes = self.__filter_nodes(nodes, 'state', options.state)

        if options.softwareProfile:
            nodes = self.__filter_nodes(nodes, ['softwareprofile', 'name'], options.softwareProfile)

        if options.hardwareProfile:
            nodes = self.__filter_nodes(nodes, ['hardwareprofile', 'name'], options.hardwareProfile)

        grouped: Dict[str, List[Dict[str, Any]]] = self.__group_nodes(nodes, options.bByHardwareProfile)

        if options.bShortOutput:
            output: Optional[str] = self.__make_short_output(grouped)
        elif options.bListOutput:
            output: Optional[str] = self.__make_list_output(nodes)
        else:
            output: Optional[str] = self.__make_full_output(grouped)

        print(output)

    @staticmethod
    def __filter_nodes(nodes: List[Dict[str, Any]], filter_key: Union[List[str], str], filter_value: Any,
                       if_not: bool = False) -> List[Dict[str, Any]]:
        """
        Filter from nodes list (list
        is mutated, thus not returned).

        :param nodes: List
        :param filter_key: List or String
        :param filter_value: Object
        :param if_not: Boolean
        :return: None
        """
        filtered: list = []

        for node in nodes:
            if type(filter_key) is str:
                result: bool = node[filter_key] == filter_value
            else:
                result: bool = node[filter_key[0]][filter_key[1]] == filter_value

            if not result == if_not:  # Switches based on `if_not`.
                filtered.append(node)

        return filtered

    @staticmethod
    def __group_nodes(nodes: List[Dict[str, Any]], by_hardware_profile: bool) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group nodes by software (default) or
        hardware profile.
        :param nodes: List
        :param by_hardware_profile: Boolean
        :return: Dictionary
        """
        grouped: dict = {}
        profile: str = 'hardwareprofile' if by_hardware_profile else 'softwareprofile'
        for node in nodes:
            key: str = node[profile]['name']
            if key not in grouped.keys():
                grouped[key]: list = []
            grouped[key].append(node)

        return grouped

    @staticmethod
    def __make_header(title: str, length: int = 80) -> str:
        """
        Pad headers to the same size.

        :param title: String
        :param length: Integer total length
        :return: String
        """
        return '{} {}'.format(
            title,
            ''.join(['-' for x in range(length - len(title))])
        )

    def __make_full_output(self, grouped: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Take a list of node names
        and return a formatted string
        to print.

        :param grouped: List Dictionary
        :return: String
        """
        output: List[str] = []

        for profile in grouped.keys():
            output.append(self.__make_header(profile))
            output.append('')
            for node in grouped[profile]:
                if node.get('nics'):
                    output.append('{} ({})'.format(node['name'], node['nics'][0].getIp()))
                else:
                    output.append(node['name'])
                output.append('    Hardware Profile: {}'.format(node['hardwareprofile']['name']))
                output.append('    Boot: {}'.format(self.__boot_map[node['bootFrom']]))
                output.append('    Status: {}/{}, Locked: {}'.format(
                    node['state'], self.__active_map[node['isIdle']], node['lockedState']
                ))
                output.append('')

        return '\n'.join(output)

    def __make_short_output(self, grouped: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Take a list of node names
        and return a formatted string
        to print.

        :param grouped: Dictionary List
        :return: String
        """
        output: List[str] = []

        for profile in grouped.keys():
            output.append(self.__make_header(profile))
            output.append('')
            for node in grouped[profile]:
                output.append('{} ({})'.format(node['name'], node['state']))

            output.append('')

        return '\n'.join(output)

    @staticmethod
    def __make_list_output(nodes: List[Dict[str, Any]]) -> str:
        """
        Take a list of node names
        and return a formatted string
        to print.

        :param nodes: List String
        :return: String
        """
        output: List[str] = []

        for node in nodes:
            output.append(node['name'])

        return '\n'.join(output)


def main():
    GetNodeStatus().run()
