import argparse
import asyncio
import json
import ssl
import sys
import websockets

import yaml

from ..base import Command


class ListenCommand(Command):
    def execute(self, args: argparse.Namespace):
        """
        Listen for events on the Tortuga websocket and print them to
        stdout.

        """
        cli = self.parent

        url = '{}://{}:{}'.format(
            cli.config_manager.getWebsocketScheme(),
            cli.config_manager.getInstaller(),
            cli.config_manager.getWebsocketPort()
        )

        ws_client = WebsocketClient(username=cli.username,
                                    password=cli.password,
                                    url=url)

        try:
            asyncio.get_event_loop().run_until_complete(ws_client.start())

        except KeyboardInterrupt:
            sys.exit(0)


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
            ssl_context.load_verify_locations(
                '/etc/pki/tls/certs/ca-bundle.crt')
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
