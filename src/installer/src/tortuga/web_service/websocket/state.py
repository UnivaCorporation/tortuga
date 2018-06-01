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

from datetime import datetime, timedelta
from typing import List, Union, Optional

from tortuga.events.types import BaseEvent
from tortuga.events.pubsub import EventPubSub
from .messages import BaseMessage


class State:
    """
    The class that represents the current state for a websocket session.

    """
    AUTHENTICATION_TIMEOUT = 30  # Seconds

    def __init__(self):
        """
        Initializer.

        """
        #
        # Authentication state
        #
        self.authenticated: bool = False
        self.username: bool = None
        self._authentication_timeout: datetime = None

        #
        # Message queue state
        #
        self._message_queue: List[Union[BaseMessage, BaseEvent]] = []
        self.pubsub: EventPubSub = None

        #
        # Websocket state
        #
        self.exit: bool = False
        self.exit_reason: str = None

    def start_authentication_timeout(self):
        """
        Sets the current authentication timeout to the amount specified by
        AUTHENTICATION_TIMEOUT.

        """
        self._authentication_timeout = datetime.now() + \
                timedelta(seconds=self.AUTHENTICATION_TIMEOUT)

    def clear_authentication_timeout(self):
        """
        Clears any authentication timeout that is currently set.

        """
        self._authentication_timeout = None

    def is_authentication_timed_out(self) -> bool:
        """
        Determines whether or not the authentication period has expired.

        :returns bool: True if the period has timed out, False otherwise

        """
        if self._authentication_timeout and \
                datetime.now() >= self._authentication_timeout:
            return True
        return False

    def enqueue_message(self, msg: Union[BaseMessage, BaseEvent]):
        """
        Enqueues a message to be sent to the websocket client.

        :param Union[BaseMessage, BaseEvent] msg: the message to send

        """
        self._message_queue.insert(0, msg)

    def next_message(self) -> Optional[Union[BaseMessage, BaseEvent]]:
        """
        Gets the next message to send from the queue.

        :return Optional[Union[BaseMessage, BaseEvent]]: the next message if
                                                         any, None otherwise
        """
        #
        # Queued messages take priority over pubsub messages
        #
        if self._message_queue:
            return self._message_queue.pop()

        #
        # If there are no queued messages, check for pubsub messages
        #
        if self.authenticated and self.pubsub:
            return self.pubsub.get_message()

        return None

    def clear_message_queue(self):
        """
        Clears all messages from the user and usubscribes them from any
        subscriptions.

        """
        #
        # Unsubscribe from the event pubsub
        #
        if self.pubsub:
            self.pubsub.unsubscribe()
        self.pubsub = None

        #
        # Clear out the message queue
        #
        self._message_queue = []
