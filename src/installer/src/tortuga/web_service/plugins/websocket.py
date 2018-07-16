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

import asyncio
import logging
import os
import ssl
import threading

import cherrypy
from cherrypy.process import plugins
import websockets

from tortuga.config.configManager import ConfigManager
from tortuga.web_service.websocket.state_manager import StateManager


logger = logging.getLogger(__name__)


class WebsocketPlugin(plugins.SimplePlugin):
    """
    A CherryPy plugin that opens a websocket for sending event notifications.

    """
    def __init__(self, bus):
        super().__init__(bus)
        self._cm = ConfigManager()
        self._loop: asyncio.AbstractEventLoop = None
        self._thread: threading.Thread = None

    def start(self):
        self._thread = threading.Thread(target=self.worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._loop.stop()

    def worker(self):
        """
        The thread worker that runs the asyncio event loop for handling
        websockets.

        """
        logger.debug('Starting websocket server thread')

        #
        # Create a new asyncio event loop for the thread
        #
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        scheme = self._cm.getWebsocketScheme()
        port = self._cm.getWebsocketPort()

        try:
            if scheme == 'wss':
                server = self._start_secure(port=port)

            elif scheme == 'ws':
                server = self._start_insecure(port=port)

            else:
                raise Exception('Unknown websocket scheme: {}'.format(scheme))

        except Exception as ex:
            logger.error(str(ex))
            logger.error('Unable to start websocket server')

            return

        self._loop.run_until_complete(server)
        self._loop.run_forever()

    def _start_secure(self, port: int) -> websockets.WebSocketServerProtocol:
        logger.debug(
            'Starting websocket with SSL/TLS enabled on port {}'.format(port))

        ssl_context = self._get_ssl_context()

        return websockets.serve(websocket_handler, port=port, ssl=ssl_context)

    def _get_ssl_context(self) -> ssl.SSLContext:
        cherrypy_cert = cherrypy.config.get('server.ssl_certificate', '')
        cherrypy_key = cherrypy.config.get('server.ssl_private_key', '')
        websocket_cert = cherrypy_cert.replace('.crt', '-bundle.crt')

        if not os.path.exists(websocket_cert):
            raise Exception(
                'Combined SSL cert not found: {}'.format(websocket_cert))

        if not os.path.exists(cherrypy_key):
            raise Exception('SSL key not found: {}'.format(cherrypy_key))

        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(websocket_cert, keyfile=cherrypy_key)
        ssl_context.verify_mode = ssl.CERT_OPTIONAL
        ssl_context.load_verify_locations('/etc/pki/tls/certs/ca-bundle.crt')

        return ssl_context

    def _start_insecure(self, port: int) -> websockets.WebSocketServerProtocol:
        logger.debug(
            'Starting websocket with SSL/TLS disabled on port {}'.format(
                port))

        return websockets.serve(websocket_handler, port=port)


async def websocket_handler(websocket, path):
    """
    The main websocket handler.

    :param websocket: the websocket server instance
    :param path:      the path requested on the websocket (unused)

    """
    logger.debug('New websocket connection established')

    try:
        state_manager = StateManager(websocket=websocket)
        consumer_task = asyncio.ensure_future(
            state_manager.consumer_handler())
        producer_task = asyncio.ensure_future(
            state_manager.producer_handler())

    except Exception as ex:
        logger.error(str(ex))
        logger.error('Websocket connection exited')
        raise

    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    logger.debug('Websocket connection exited')
