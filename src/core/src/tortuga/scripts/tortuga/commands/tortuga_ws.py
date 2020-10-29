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
import json
import os
from typing import List, Dict

import yaml

from tortuga.cli.base import Argument, RootCommand, Command
from tortuga.cli.utils import pretty_print
from tortuga.wsapi_v2.client import TortugaWsApiClient
from ..script import TortugaScriptConfig


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
        endpoint: str = self.parent.endpoint

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        config: TortugaScriptConfig = self.get_config()
        ws_client = get_client(config, self.parent.endpoint)

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
        endpoint: str = self.command.parent.endpoint
        #
        # Remove pluralization if found, as this argument represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)


class GetCommand(Command):
    """
    This command gets a specific item on an API endpoint.

    """
    name = 'get'
    help = 'Get a single {}'

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
        endpoint: str = self.parent.endpoint
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        config: TortugaScriptConfig = self.get_config()
        ws_client: TortugaWsApiClient = get_client(config, self.parent.endpoint)
        pretty_print(ws_client.get(args.id[0]), args.fmt)


class CreateUpdateMixin:
    def _load_data(self, filename) -> dict:
        if not os.path.exists(filename):
            raise Exception('File not found: {}'.format(filename))

        _, ext = os.path.splitext(filename)
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

        with open(filename) as fp:
            loader = getattr(self, '_load_{}'.format(ext))
            data = loader(fp)

        return data

    @staticmethod
    def _load_json(fp) -> dict:
        return json.load(fp)

    @staticmethod
    def _load_yaml(fp) -> dict:
        return yaml.safe_load(fp)


class CreateCommand(CreateUpdateMixin, Command):
    """
    This command creates a specific item on an API endpoint.

    """
    name = 'create'
    help = 'Create a {}'

    arguments = [
        TortugaWsArgument(
            'file',
            type=str,
            nargs=1,
            help='Path to the {} create file'
        )
    ]

    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.parent.endpoint
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        config: TortugaScriptConfig = self.get_config()
        ws_client: TortugaWsApiClient = get_client(config, self.parent.endpoint)

        obj_filename = args.file[0]
        data = self._load_data(obj_filename)

        pretty_print(ws_client.post(data), args.fmt)


class UpdateCommand(CreateUpdateMixin, Command):
    """
    This command updates a specific item on an API endpoint.

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
        endpoint: str = self.parent.endpoint
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        config: TortugaScriptConfig = self.get_config()
        ws_client: TortugaWsApiClient = get_client(config, self.parent.endpoint)

        obj_filename = args.file[0]
        data = self._load_data(obj_filename)

        pretty_print(ws_client.put(data), args.fmt)


class DeleteCommand(Command):
    """
    This command deletes a specific item on an API endpoint.

    """
    name = 'delete'
    help = 'Delete a {}'

    arguments = [
        TortugaWsArgument(
            'id',
            type=str,
            nargs=1,
            help='ID of the {} to delete'
        )
    ]

    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.parent.endpoint
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        config: TortugaScriptConfig = self.get_config()
        ws_client: TortugaWsApiClient = get_client(config, self.parent.endpoint)
        ws_client.delete(args.id[0])


class EventsCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'events'
    help = 'Tortuga events API'

    sub_commands = [
        ListCommand(),
        GetCommand(),
    ]


class HardwareProfilesCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'hardwareprofiles'
    help = 'Tortuga hardware profiles API'

    sub_commands = [
        ListCommand(),
        GetCommand(),
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
        GetCommand(),
        UpdateCommand(),
    ]


class ResourceRequestCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'resourcerequests'
    help = 'Tortuga resource requests API'

    sub_commands = [
        ListCommand(),
        GetCommand(),
        CreateCommand(),
        UpdateCommand(),
        DeleteCommand()
    ]


class SoftwareProfilesCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'softwareprofiles'
    help = 'Tortuga software profiles API'

    sub_commands = [
        ListCommand(),
        GetCommand(),
        UpdateCommand(),
    ]


class TagsCommand(RootCommand):
    """
    This is a command for interacting with WS API endpoints.

    """
    name = 'tags'
    help = 'Tortuga tags API'

    sub_commands = [
        ListCommand(),
        GetCommand(),
        CreateCommand(),
        UpdateCommand(),
        DeleteCommand(),
    ]


def get_client(config: TortugaScriptConfig,
               endpoint: str) -> TortugaWsApiClient:
    """
    Gets a configured TortugaWsClient for the specified endpoint.

    :param TortugaScriptConfig config: the current config
    :param str endpoint:               the API endpoint

    :return TortugaWsApiClient: the configured client instance

    """
    if not config:
        raise Exception('Invalid configuration')

    auth_method = config.get_auth_method()

    if auth_method == config.AUTH_METHOD_PASSWORD:
        return TortugaWsApiClient(
            endpoint=endpoint,
            username=config.username,
            password=config.password,
            base_url=config.url,
            verify=config.verify
        )

    if auth_method == config.AUTH_METHOD_TOKEN:
        return TortugaWsApiClient(
            endpoint=endpoint,
            token=config.get_token(),
            base_url=config.url,
            verify=config.verify
        )

    raise Exception('Unsupported auth method: {}'.format(auth_method))
