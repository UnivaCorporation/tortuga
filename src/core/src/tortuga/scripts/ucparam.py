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

"""
Command-line utility for manipulating the Tortuga global parameters
database

"""

import sys

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.objects.parameter import Parameter
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.wsapi.parameterWsApi import ParameterWsApi


class UcParam(TortugaCli):
    def __init__(self):
        super().__init__()
        self._api = None

        self.getParser().add_argument('--debug', action='store_true',
                                      help='Enable debug logging')
        self.getParser().add_argument('--verbose', action='store_true',
                                      help='Enable verbose logging')

        subparsers = self.getParser().add_subparsers()

        # Initialize 'get' subparser
        parser_get = subparsers.add_parser('get')
        parser_get.set_defaults(subcommand='get')

        parser_get.add_argument('name')

        # Initialize 'set' subparser
        self._parser_set = subparsers.add_parser('set')
        self._parser_set.set_defaults(subcommand='set')

        self._parser_set.add_argument('name', nargs='?', metavar='name')
        self._parser_set.add_argument('value', nargs='?', metavar='value')

        # Initialize 'delete' subparser
        parser_delete = subparsers.add_parser('delete')
        parser_delete.set_defaults(subcommand='delete')

        parser_delete.add_argument('name')

        # Initialize 'list' subparser
        parser_list = subparsers.add_parser(
            'list', help='List all Tortuga parameters')
        parser_list.set_defaults(subcommand='list')

        # Initialize 'export' subparser
        parser_export = subparsers.add_parser(
            'export', help='Export all user-defined parameters')
        parser_export.set_defaults(subcommand='export')

    def get_api(self):
        if not self._api:
            self._api = ParameterWsApi(username=self.getUsername(),
                                       password=self.getPassword(),
                                       baseurl=self.getUrl())
        return self._api

    def runCommand(self):
        self.parseArgs()
        args = self.getArgs()

        if hasattr(args, 'subcommand'):
            action = args.subcommand.lower()

            if action == 'get':
                self._get_action(args.name)
            elif action == 'set':
                self._set_action(self._parser_set, args.name, args.value)
            elif action == 'delete':
                self._delete_action(args.name)
            elif action == 'list':
                self._list_action()
            elif action == 'export':
                self._export_action()

    def _get_action(self, name):
        """
        Retrieve parameter from database

        """
        try:
            print(self.get_api().getParameter(name).getValue())
        except ParameterNotFound:
            sys.exit(1)

    def _set_parameter(self, name, value):
        """
        Sets the value of a parameter.

        :param name:  the name of the parameter to set
        :param value: the value of the parameter to set

        """
        try:
            parameter = self.get_api().getParameter(name)
            parameter.setValue(value)
            self.get_api().updateParameter(parameter)

        except ParameterNotFound:
            parameter = Parameter(name=name, value=value)
            self.get_api().createParameter(parameter)

    def _set_action(self, parser, name, value):
        """
        Set parameters

        """
        if name is None and value is None:
            if not sys.stdin.isatty():
                lineno = 0
                for entry in sys.stdin.readlines():
                    lineno += 1
                    if entry.startswith('#'):
                        continue
                    try:
                        name, value = entry.rstrip().split(' ', 1)
                        self._set_parameter(name, value.lstrip())
                    except ValueError:
                        sys.stderr.write(
                            'Ignoring malformed line #%d\n' % (lineno))
                return
            else:
                parser.print_help()
                sys.exit(1)

        if value is None:
            parser.error('Value must be specified for name [%s]' % (name))

        self._set_parameter(name, value)

    def _delete_action(self, name):
        """
        Delete parameter

        """
        self.get_api().deleteParameter(name)

    def _list_action(self):
        """
        List all parameters

        """
        for item in self.get_api().getParameterList():
            print('%s: %s' % (item.getName(), item.getValue()))

    def _export_action(self):
        for item in self.get_api().getParameterList():
            if item.getName() in ('Language', 'Keyboard', 'Timezone_zone',
                                  'Timezone_utc', 'DbSchemaVers',
                                  'IntWebPort', 'IntWebServicePort',
                                  'WebservicePort', 'EulaAccepted',
                                  'DNSZone',):
                # Ignore any Tortuga default settings
                continue
            print('%s %s' % (item.getName(), item.getValue()))


def main():
    UcParam().run()
