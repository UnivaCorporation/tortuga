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
import asyncio
import configparser
import json
import logging
import os
import ssl
import sys
from typing import Dict, List

import websockets
import yaml

from tortuga.config.configManager import ConfigManager
from tortuga.wsapi_v2.client import TortugaWsApiClient


logger = logging.getLogger(__name__)


class Tortuga:
    def __init__(self):
        logger.addHandler(logging.NullHandler())

        self._parser: argparse.ArgumentParser = argparse.ArgumentParser()
        self._args: object = None
        self._url: str = None
        self._username: str = None
        self._password: str = None
        self._cm: ConfigManager = ConfigManager()

    def initialize_options(self):
        """
        Initialize command line arguments/options.

        """
        self._parser.add_argument(
            'cmd',
            type=str,
            nargs='*',
            help='Command, action, and arguments (i.e. events list)'
        )

        self._parser.add_argument(
            '-q', '--query',
            type=str,
            nargs='*',
            help='Query parameters for command, if applicable'
        )

        self._parser.add_argument(
            '-v', '--version',
            action='store_true',
            dest='version',
            default=False,
            help='print version and exit'
        )

        self._parser.add_argument(
            '-d', '--debug',
            dest='debug',
            help='set debug level; valid values are: critical, error, '
                 'warning, info, debug'
        )

        self._parser.add_argument(
            '--url',
            help='Tortuga web service URL'
        )

        self._parser.add_argument(
            '--username',
            dest='username',
            help='Tortuga web service user name'
        )

        self._parser.add_argument(
            '--password',
            dest='password',
            help='Tortuga web service password'
        )

    def parse_args(self) -> argparse.Namespace:
        """
        Parse command line.

        :return argparse.Namespace: the parsed arguments.

        """
        try:
            self._args = self._parser.parse_args()
        except SystemExit as rc:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(int(str(rc)))

        self._version()
        self._set_log_level()
        self._set_web_service_params()

        return self._args

    def _version(self):
        """
        Implements the --version argument.

        """
        if self._args.version:
            print(
                '{0} version: {1}'.format(
                    os.path.basename(sys.argv[0]),
                    self._cm.getTortugaRelease()
                )
            )
            sys.exit(0)

    def _set_log_level(self):
        """
        Implements the --debug argument.

        """
        if self._args.debug:
            root_logger = logging.getLogger('tortuga')
            root_logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            root_logger.addHandler(ch)

    def _set_web_service_params(self):
        """
        Processes the --username --password and --url arguments.

        """
        url, username, password = self._get_web_service_options()
        self._url = url
        self._username = username
        self._password = password

    def _get_web_service_options(self):
        """
        Read Tortuga web service credentials from config file, environment,
        or command-line. Command-line overrides either config file or
        environment.

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

        if self._args.url:
            url = self._args.url
        elif os.getenv('TORTUGA_WS_URL'):
            url = os.getenv('TORTUGA_WS_URL')

        if self._args.username:
            username = self._args.username
        elif os.getenv('TORTUGA_WS_USERNAME'):
            username = os.getenv('TORTUGA_WS_USERNAME')

        if self._args.password:
            password = self._args.password
        elif os.getenv('TORTUGA_WS_PASSWORD'):
            password = os.getenv('TORTUGA_WS_PASSWORD')

        if username is None and password is None:
            logger.debug('Using built-in user credentials')
            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()

        return url, username, password

    def run(self):
        """
        Runs the command-line utility.

        """
        try:
            self._run()
        except Exception as ex:
            print(ex)
            raise SystemExit(-1)
        except SystemExit:
            raise

    def _run(self):
        """
        Really runs the command-line utility.

        """
        self.initialize_options()
        args = self.parse_args()

        cmd = args.cmd
        if cmd:
            self._run_cmd(cmd, args.query)

    def _run_cmd(self, cmd: List[str], query: List[str]):
        """
        Runs the command list passed in to the command line utility.

        :param List[str] cmd:   the list of positional command line arguments
        :param List[str] query: the list of query arguments passed in via
                                the --query option

        """
        if not cmd:
            cmd = []

        if not query:
            query = []

        if cmd and cmd[0] == 'listen':
            self._listen()
            sys.exit(0)

        if len(cmd) == 1:
            print('Command action is required')
            raise SystemExit(-1)

        ws = TortugaWsApiClient(endpoint=cmd[0])
        params = self._parse_params(query)
        if cmd[1] == 'list':
            pretty_print(ws.list(**params))
        elif cmd[1] == 'show':
            pretty_print(ws.get(cmd[2]))

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

    def _listen(self):
        """
        Listen for events on the Tortuga websocket and print them to
        stdout.

        """
        url = '{}://{}:{}'.format(
            self._cm.getWebsocketScheme(),
            self._cm.getInstaller(),
            self._cm.getWebsocketPort()
        )

        ws_client = WebsocketClient(username=self._username,
                                    password=self._password,
                                    url=url)

        try:
            asyncio.get_event_loop().run_until_complete(ws_client.start())

        except KeyboardInterrupt:
            sys.exit(0)


def pretty_print(data):
    """
    Outputs data as nicely formatted YAML.

    :param data: A Python data structure

    """
    print(yaml.safe_dump(data, default_flow_style=False))


class WebsocketClient:
    """
    Websocket client class.

    """
    def __init__(self, username: str, password: str, url: str):
        self._username = username
        self._password = password
        self._url = url
        self._websocket = None

    async def start(self):
        """
        Initializes the websocket and starts the event loop.

        """
        if self._url.startswith('wss:'):
            ssl_context = ssl.SSLContext()
            ssl_context.verify_flags = ssl.CERT_NONE
        else:
            ssl_context = None

        async with websockets.connect(self._url, ssl=ssl_context) as ws:
            await self.send_recieve(ws)

    async def send_recieve(self, ws: websockets.WebSocketClientProtocol):
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print(yaml.safe_dump(data, default_flow_style=False))

            if data['type'] == 'message':
                if data['name'] == 'authentication-required':
                    await self.send_auth(ws)

                if data['name'] == 'authentication-succeeded':
                    await self.send_subscribe(ws)

    async def send_auth(self, ws: websockets.WebSocketClientProtocol):
        """
        Sends an authentication request.

        """
        data = {
            'action': 'authenticate',
            'method': 'password',
            'data': {
                'username': self._username,
                'password': self._password
            }
        }

        await ws.send(json.dumps(data))

    async def send_subscribe(self, ws: websockets.WebSocketClientProtocol):
        """
        Sends a subscription request.

        """
        data = {
            'action': 'subscribe'
        }

        await ws.send(json.dumps(data))


def main():
    """
    Main.

    """
    Tortuga().run()
