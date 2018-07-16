import argparse
from typing import List, Dict

import yaml

from tortuga.wsapi_v2.client import TortugaWsApiClient
from ..base import Argument, Command


class ListCommand(Command):
    """
    This command lists all items on an API endpoint.

    """
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
        endpoint: str = self.parent.args[0]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        ws_client = self.parent.ws_client

        query = args.query
        if not query:
            query = []

        params = self._parse_params(query)

        pretty_print(ws_client.list(**params))

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


class IdArgument(Argument):
    def get_help(self):
        #
        # Since this class can be used for multiple endpoints, we want to
        # customize the help text by inserting the endpoint name as
        # required
        #
        endpoint: str = self.command.parent.args[0]
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
    arguments = [
        IdArgument(
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
        endpoint: str = self.parent.args[0]
        #
        # Remove pluralization if found, as this command represents
        # a single entity
        #
        if endpoint.endswith('s'):
            endpoint = endpoint[0:-1]

        return super().get_help().format(endpoint)

    def execute(self, args: argparse.Namespace):
        ws_client = self.parent.ws_client

        pretty_print(ws_client.get(args.id))


class TortugaWsCommand(Command):
    """
    This is a command for interacting with WS API endpoints.

    """
    commands = [
        ListCommand(
            'list',
            help='List all {}'
        ),
        ShowCommand(
            'show',
            help='Show a single {}'
        )
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # Configure the web service endpoint for all sub commands
        #
        self.ws_client = TortugaWsApiClient(args[0])


def pretty_print(data):
    """
    Outputs data as nicely formatted YAML.

    :param data: A Python data structure

    """
    print(yaml.safe_dump(data, default_flow_style=False))
