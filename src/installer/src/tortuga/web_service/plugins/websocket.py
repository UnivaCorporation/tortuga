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
import json
import logging
import threading

from cherrypy.process import plugins
import websockets

from tortuga.events.manager import PubSubManager


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
        logging.debug('Starting websocket server thread')

        #
        # Create a new asyncio event loop for the thread
        #
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        #
        # Start the websockets server
        #
        server = websockets.serve(subcribe_to_events, port=9443)
        self._loop.run_until_complete(server)
        self._loop.run_forever()


@asyncio.coroutine
def subcribe_to_events(websocket: websockets.WebSocketServerProtocol,
                       path: str):
    """
    Subscribes to events, and sends them as JSON data over the websocket.

    :param websockets.WebSocketServerProtocol websocket:
    :param websocket URI path:

    """
    logging.debug('New websocket connection established')

    #
    # Subscribe to the events pub/sub service
    #
    pubsub = PubSubManager.get()
    pubsub.subscribe()
    while True:
        #
        # Get the next event, if any
        #
        event = pubsub.get_message()
        #
        # If there is an event, send it immediately
        #
        if event:
            event_dict = event.schema().dump(event).data
            yield from websocket.send(json.dumps(event_dict))
        #
        # If there is are no events in the queue, return to the main event
        # loop so as to not block processing
        #
        else:
            yield from asyncio.sleep(1)
