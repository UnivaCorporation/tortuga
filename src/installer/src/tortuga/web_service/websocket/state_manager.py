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
from typing import Type, Union

import websockets
from marshmallow import UnmarshalResult

from tortuga.events.types import BaseEvent
from tortuga.logging import WEBSERVICE_NAMESPACE
from .actions import BaseAction, get_action_class
from .exceptions import AuthenticationRequired, ActionNotFoundError
from .messages import BaseMessage, AuthenticationRequiredMessage, ErrorMessage
from .state import State


logger = logging.getLogger(WEBSERVICE_NAMESPACE)


class StateManager:
    """
    A class for managing the inbound/outbound messages and state of a
    websocket session.

    """
    def __init__(self, websocket: websockets.WebSocketServerProtocol):
        """
        Initializer.

        """
        logger.debug('Initializing websocket state manager')
        self._websocket = websocket
        self.state = State()
        #
        # Enqueue an authentication message to be sent immediately upon
        # the websocket session being established
        #
        self.state.enqueue_message(AuthenticationRequiredMessage())
        self.state.start_authentication_timeout()

    async def consumer_handler(self):
        """
        This is the primary asynchronous method that is used for handling
        inbound websocket massages.

        """
        logger.debug('Starting websocket consumer')

        #
        # Main inbound message handling loop
        #
        while not self.state.exit:
            msg = await self._websocket.recv()
            await self.consumer(json.loads(msg))

        #
        # If we get this far, that means the state had it's exit flag set,
        # so we close the connection nicely and state the reason, if any
        #
        await self._websocket.close(reason=self.state.exit_reason)

    async def consumer(self, inbound_message: dict):
        """
        Handles a single inbound message.

        :param dict inbound_message: the inbound message to handle

        """
        action_name = inbound_message.get('action', None)

        try:
            #
            # Get an instance of the action class based on the action_name
            #
            action_class: Type[BaseAction] = get_action_class(action_name)
            unmarshalled: UnmarshalResult = \
                action_class.schema().load(inbound_message)
            action: BaseAction = action_class(state=self.state,
                                              **unmarshalled.data)

            #
            # Assuming we have a valid action class, we "do" the action
            #
            action.do()

        #
        # Handle all the bad things that could happen...
        #
        except ActionNotFoundError:
            msg = 'Unknown action: {}'.format(action_name)
            self.state.enqueue_message(ErrorMessage(reason=msg))

        #
        # Actions are responsible for deciding whether or not authentication
        # is required and raising the appropriate exception if the user
        # is not logged in.
        #
        except AuthenticationRequired:
            self.state.enqueue_message(AuthenticationRequiredMessage())

        #
        # Everything else is sent down as a general error
        #
        except Exception as ex:
            self.state.enqueue_message(ErrorMessage(reason=str(ex)))

    async def producer_handler(self):
        """
        This is the primary asynchronous method that is used for handling
        outbound websocket massages.

        """
        logger.debug('Starting websocket producer')

        #
        # Main outbound message handling loop
        #
        while not self.state.exit:
            msg: Union[BaseMessage, BaseEvent] = await self.producer()
            marshalled = msg.schema().dump(msg)
            await self._websocket.send(json.dumps(marshalled.data))

        #
        # If we get this far, that means the state had it's exit flag set,
        # so we close the connection nicely and state the reason, if any
        #
        await self._websocket.close(reason=self.state.exit_reason)

    async def producer(self) -> Union[BaseMessage, BaseEvent]:
        """
        Gets the next outbound message.

        :returns Union[BaseMessage, BaseEvent]: the next outbound message to
                                                send

        """
        msg: Union[BaseMessage, BaseEvent] = None

        #
        # This loops spins until there is a message to return
        #
        while not msg:
            #
            # Every time around the loop, we make sure that there are
            # no authentication anomalies to deal with.
            #
            # If we have hit an authentication timeout, we clear the message
            # queue, and set the state to exit, set the reason, and send
            # a final message down the pipe.
            #
            if self.state.is_authentication_timed_out():
                self.state.clear_message_queue()
                self.state.exit = True
                self.state.exit_reason = 'Authentication timeout'
                self.state.enqueue_message(
                    ErrorMessage(reason='Authentication timeout')
                )

            msg = self.state.next_message()

            #
            # If there is no message to send, we wait for a short period of
            # time before trying again.
            #
            if not msg:
                await asyncio.sleep(1)

        return msg
