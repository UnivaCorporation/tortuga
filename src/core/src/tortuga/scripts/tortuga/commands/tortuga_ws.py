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

import argparse
import configparser
import json
import os
from typing import List, Dict

import yaml

from tortuga.cli.base import Argument, RootCommand, Command
from tortuga.cli.utils import pretty_print
from tortuga.config.configManager import ConfigManager
from tortuga.wsapi_v2.client import TortugaWsApiClient


SUPPORTED_FILE_TYPES = ['yaml', 'json']


class ListCommand(Command):
    """
    This command lists all items on an API endpoint.

    """
    name = 'list'
    help = 'List all {}'

    arguments = [
        Argument(
            '-q', '--query',
            type=str,
            nargs='*',
            help='List query parameters'
        )
    ]

    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.parent.name

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        ws_client = get_client(args, self.parent.name)

        query = args.query
        if not query:
            query = []

        params = self._parse_params(query)

        pretty_print(ws_client.list(**params), args.fmt)

    def _parse_params(self, query: List[str]) -> Dict[str, str]:
        """
        Takes a list of --query parameters and turns them into a dict
        suitable for passing to a funtion as **kwargs

        :param List[str] query: a list of "key=value" query arguments to
                                to parse

        :return Dict[str, str]: a dictionary of {key: value} pairs

        """
        params = {}
        for q in query:
            parts = q.split('=')
            params[parts[0]] = parts[1]

        return params


class TortugaWsArgument(Argument):
    """
    An argument that outputs the help text to match the name of the Tortuga
    web service endpoint.

    """
    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.command.parent.name
        #
        # Remove pluralization if found, as this argument represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)


class ShowCommand(Command):
    """
    This command shows a specific item on an API endpoint.

    """
    name = 'show'
    help = 'Show a single {}'

    arguments = [
        TortugaWsArgument(
            'id',
            type=str,
            nargs=1,
            help='Id of the {} to get'
        )
    ]

    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.parent.name
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        ws_client: TortugaWsApiClient = get_client(args, self.parent.name)

        pretty_print(ws_client.get(args.id[0]), args.fmt)


class UpdateCommand(Command):
    """
    This command shows a specific item on an API endpoint.

    """
    name = 'update'
    help = 'Update a {}'

    arguments = [
        TortugaWsArgument(
            'file',
            type=str,
            nargs=1,
            help='Path to the {} update file'
        )
    ]

    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.parent.name
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        ws_client: TortugaWsApiClient = get_client(args, self.parent.name)

        obj_filename = args.file[0]
        if not os.path.exists(obj_filename):
            raise Exception('File not found: {}'.format(obj_filename))

        _, ext = os.path.splitext(obj_filename)
        if not ext:
            raise Exception(
                'File extension not valid. Supported file types: {}'.format(
                    SUPPORTED_FILE_TYPES
                ))

        ext = ext[1:]
        if ext not in SUPPORTED_FILE_TYPES:
            raise Exception(
                'File extension not valid. Supported file types: {}'.format(
                    SUPPORTED_FILE_TYPES
                ))

        with open(obj_filename) as fp:
            loader = getattr(self, '_load_{}'.format(ext))
            data = loader(fp)

        pretty_print(ws_client.put(data), args.fmt)

    @staticmethod
    def _load_json(fp) -> dict:
        return json.load(fp)

    @staticmethod
    def _load_yaml(fp) -> dict:
        return yaml.safe_load(fp)


class EventsCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'events'
    help = 'Tortuga events API'

    sub_commands = [
        ListCommand(),
        ShowCommand(),
    ]


class HardwareProfilesCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'hardwareprofiles'
    help = 'Tortuga hardware profiles API'

    sub_commands = [
        ListCommand(),
        ShowCommand(),
        UpdateCommand(),
    ]


class NodesCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'nodes'
    help = 'Tortuga nodes API'

    sub_commands = [
        ListCommand(),
        ShowCommand(),
        UpdateCommand(),
    ]


class SoftwareProfilesCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'softwareprofiles'
    help = 'Tortuga software profiles API'

    sub_commands = [
        ListCommand(),
        ShowCommand(),
        UpdateCommand(),
    ]


def get_web_service_config(args: argparse.Namespace):
    """
    Gets url, username, and password for the Tortuga web service.

    :param argparse.Namespace args: argparse Namespace instance

    :return tuple: (url, username, password)

    """
    username = password = url = None

    cfg_file = os.path.join(os.path.expanduser('~'),
                            '.local',
                            'tortuga',
                            'credentials')

    if os.path.exists(cfg_file):
        cfg = configparser.ConfigParser()

        cfg.read(cfg_file)

        username = cfg.get('default', 'username') \
            if cfg.has_section('default') and \
            cfg.has_option('default', 'username') else None

        password = cfg.get('default', 'password') \
            if cfg.has_section('default') and \
            cfg.has_option('default', 'password') else None

        url = cfg.get('default', 'url') \
            if cfg.has_section('default') and \
            cfg.has_option('default', 'url') else None

    if args.url:
        url = args.url
    elif os.getenv('TORTUGA_WS_URL'):
        url = os.getenv('TORTUGA_WS_URL')

    if args.username:
        username = args.username
    elif os.getenv('TORTUGA_WS_USERNAME'):
        username = os.getenv('TORTUGA_WS_USERNAME')

    if args.password:
        password = args.password
    elif os.getenv('TORTUGA_WS_PASSWORD'):
        password = os.getenv('TORTUGA_WS_PASSWORD')

    #
    # CLI arguments should override the environment variable
    #
    if os.getenv('TORTUGA_WS_NO_VERIFY'):
        verify = False
    else:
        verify = args.verify

    if username is None and password is None:
        cm = ConfigManager()
        username = cm.getCfmUser()
        password = cm.getCfmPassword()

    return url, username, password, verify


def get_client(args: argparse.Namespace, endpoint: str) -> TortugaWsApiClient:
    """
    Gets a configured TortugaWsClient for the specified endpoint.

    :param argparse.Namespace args: the argparse Namespace
    :param str endpoint:            the API endpoint

    :return TortugaWsApiClient: the configured client instance

    """
    url, username, password, verify = get_web_service_config(args)

    return TortugaWsApiClient(
        endpoint=endpoint,
        username=username,
        password=password,
        base_url=url,
        verify=verify
    )
