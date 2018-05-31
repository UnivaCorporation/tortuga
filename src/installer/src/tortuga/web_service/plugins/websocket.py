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
import threading

from cherrypy.process import plugins
import websockets

from tortuga.web_service.websocket.state_manager import StateManager


logger = logging.getLogger(__name__)


class WebsocketPlugin(plugins.SimplePlugin):
    """
    A CherryPy plugin that opens a websocket for sending event notifications.

    """
    def __init__(self, bus):
        super().__init__(bus)
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

        #
        # Start the websockets server
        #
        server = websockets.serve(websocket_handler, port=9443)
        self._loop.run_until_complete(server)
        self._loop.run_forever()


async def websocket_handler(websocket, path):
    """
    The main websocket handler.

    :param websocket: the websocket server instance
    :param path:      the path requested on the websocket (unused)

    """
    logger.debug('New websocket connection established')

    state_manager = StateManager(websocket=websocket)
    consumer_task = asyncio.ensure_future(state_manager.consumer_handler())
    producer_task = asyncio.ensure_future(state_manager.producer_handler())

    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    logger.debug('Websocket connection exited')
