import argparse
from logging import getLogger
from typing import Optional

import requests
import yaml

from ..base import Argument, Command


logger = getLogger(__name__)


class UnisightWsClient:
    BASE_PATH = 'UnisightService/webresources'

    def __init__(self, api: str, username: str, password: str):
        self.api = api
        if not self.api:
            raise Exception('Unisight API not set')

        self.username = username
        if not self.username:
            raise Exception('Unisight API username not set')

        self.password = password
        if not self.password:
            raise Exception('Unisight API password not set')

    def build_url(self, path) -> str:
        host = self.api
        if not host.endswith('/'):
            host += '/'

        if not path.startswith('/'):
            path = '/' + path

        return '{}{}{}'.format(
            host,
            self.BASE_PATH,
            path
        )

    def get(self, path):
        url = self.build_url(path)
        logger.debug('GET: {}'.format(url))

        result = requests.get(
            url,
            auth=(self.username, self.password),
            verify=False  # TODO: Don't ignore verification errors!
        )

        if result.status_code == 200:
            return result.json()

        else:
            raise Exception('HTTP status code: {}'.format(result.status_code))

    def list(self, path):
        return self.get(path)


class ListCommand(Command):
    def execute(self, args: argparse.Namespace):
        client: UnisightWsClient = self.parent.client

        result = client.list('rule')

        output = []
        for rule in result:
            output.append({
                'id': rule['id'],
                'name': rule['name'],
                'enabled': rule['enabled']
            })

        pretty_print(output)


class ImportCommand(Command):
    pass


class ExportCommand(Command):
    pass


class DeleteCommand(Command):
    pass


class RulesCommand(Command):
    sub_commands = [
        ListCommand(
            'list',
            help='List all rules'
        ),
        ImportCommand(
            'import',
            help='Import a rule'
        ),
        ExportCommand(
            'export',
            help='Export a rule'
        ),
        DeleteCommand(
            'delete',
            help='Delete a rule'
        )
    ]

    def __init__(self, cmd: str, config: dict, *args,
                 help: Optional[str]=None, **kwargs):
        """
        Initialize the command. The config dict requires the following
        three keys:

        {
            "api": "https://unisight.example.com:1234",
            "username": "api_username",
            "password": "api_password"
        }

        :param list args:   args, passed to the parser
        :param dict config: configuration dict
        :param help:        help text
        :param kwargs:      kwargs passed to the parser

        """
        self._client: UnisightWsClient = None
        self._config: dict = config

        super().__init__(cmd, *args, help=help, **kwargs)

    @property
    def client(self):
        """
        Lazy load the client only when it is needed.

        :return UnisightWsClient: the client instance

        """
        if not self._client:
            self._client = UnisightWsClient(
                self._config.get('api', None),
                self._config.get('username', None),
                self._config.get('password', None)
            )

        return self._client


def pretty_print(data):
    """
    Outputs data as nicely formatted YAML.

    :param data: A Python data structure

    """
    print(yaml.safe_dump(data, default_flow_style=False))
