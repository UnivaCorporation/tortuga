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
import json
import ssl
import sys
import websockets

from tortuga.cli.base import RootCommand
from tortuga.cli.utils import pretty_print
from tortuga.config.configManager import ConfigManager
from .tortuga_ws import get_web_service_config


class ListenCommand(RootCommand):
    """
    Listen command for listening to websocket events.

    """
    name = 'listen'
    help = 'Listen on the API websocket for events'

    def execute(self, args: argparse.Namespace):
        """
        Listen for events on the Tortuga websocket and print them to
        stdout.

        """
        cm = ConfigManager()

        url, username, password, verify = get_web_service_config(args)
        #
        # If we get a URL from the environment or CLI, we need to transform
        # it from the installer REST API URL into a websocket URL
        #
        if url:
            #
            # Replace http[s] with ws[s]
            #
            url = url.replace('http', 'ws')
            #
            # Replace port with websocket port
            #
            url_parts = url.split(':')
            url = '{}:{}:{}'.format(url_parts[0], url_parts[1],
                                    cm.getWebsocketPort())

        #
        # Otherwise, use the default URL from the config manager
        #
        else:
            url = '{}://{}:{}'.format(
                cm.getWebsocketScheme(),
                cm.getInstaller(),
                cm.getWebsocketPort()
            )

        ws_client = WebsocketClient(username=username,
                                    password=password,
                                    url=url,
                                    verify=verify)

        try:
            asyncio.get_event_loop().run_until_complete(ws_client.start())

        except KeyboardInterrupt:
            sys.exit(0)


class WebsocketClient:
    """
    Websocket client class.

    """
    def __init__(self, username: str, password: str, url: str,
                 verify: bool = True):
        self._username = username
        self._password = password
        self._url = url
        self._verify = verify
        self._websocket = None
        self._cm = ConfigManager()

    async def start(self):
        """
        Initializes the websocket and starts the event loop.

        """
        if self._url.startswith('wss:'):
            ssl_context = ssl.SSLContext()
            if self._verify:
                ssl_context.load_verify_locations(self._cm.getCaBundle())
            else:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = None

        async with websockets.connect(self._url, ssl=ssl_context) as ws:
            await self.send_recieve(ws)

    async def send_recieve(self, ws: websockets.WebSocketClientProtocol):
        """
        The main loop that sends/receives data.

        :param ws: the web socket client

        """
        while True:
            msg = await ws.recv()

            data = json.loads(msg)
            pretty_print(data)

            if data['type'] == 'message':
                if data['name'] == 'authentication-required':
                    await self.send_auth(ws)

                if data['name'] == 'authentication-succeeded':
                    await self.send_subscribe(ws)

    async def send_auth(self, ws: websockets.WebSocketClientProtocol):
        """
        Sends an authentication request.

        :param ws: the web socket client

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

        :param ws: the web socket client

        """
        data = {
            'action': 'subscribe'
        }

        await ws.send(json.dumps(data))
