#
# Copyright 2008-2018 Univa Corporation
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

from typing import Optional

from redis import Redis

from .types import BaseEvent
from .store import EventStore


class EventPubSub:
    """
    A publish/subscribe service for system events.

    """
    def publish(self, event: BaseEvent):
        """
        Publishes the event to the pub/sub channel.

        :param BaseEvent event: the event to publish

        """
        raise NotImplementedError()

    def subscribe(self, event_name: str = None):
        """
        Subscribes to events. Once subscribed, callse to get_message will
        check for messages.

        :param event_name: the event name to subscribe to, otherwise all

        """
        raise NotImplementedError()

    def unsubscribe(self):
        """
        Unsubscribe from the current subscription.

        """
        raise NotImplementedError()

    def get_message(self) -> Optional[BaseEvent]:
        """
        Get the next event in the queue if any.

        :returns Optional[BaseEvent]: the next event, or None

        """
        raise NotImplementedError()


class RedisEventPubSub(EventPubSub):
    _namespace = 'events'

    def __init__(self, redis_client: Redis, event_store: EventStore):
        """
        Initialization.

        :param Redis redis_client:     the (initialized) redis client to use
        :param EventSTore event_store: the (initialized) event store to use

        """
        self._redis = redis_client
        self._store = event_store
        self._pubsub = None

    def publish(self, event: BaseEvent):
        """
        See superclass.

        :param BaseEvent event:

        """
        channel = '{}.{}'.format(self._namespace, event.name)
        key = '{}:{}'.format(self._namespace, event.id)
        self._redis.publish(channel, key)

    def subscribe(self, event_name: str = None):
        """
        See superclass.

        :param str event_name:

        """
        if self._pubsub:
            raise Exception('Already subscribed')

        self._pubsub = self._redis.pubsub()

        if event_name:
            self._pubsub.subscribe('{}.{}'.format(self._namespace,
                                                  event_name))
        else:
            self._pubsub.psubscribe('{}.*'.format(self._namespace))

    def unsubscribe(self):
        """
        See superclass.

        """
        if not self._pubsub:
            return
        self._pubsub.unsubscribe()
        self._pubsub = None

    def get_message(self) -> Optional[BaseEvent]:
        """
        See superclass.

        :return Optional[BaseEvent]:

        """
        if not self._pubsub:
            raise Exception('No subscription')

        msg = self._pubsub.get_message(ignore_subscribe_messages=True)

        if not msg:
            return None

        key = msg['data'].decode()
        event_id = key.replace('{}:'.format(self._namespace), '')
        event = self._store.get(event_id)
        return event
