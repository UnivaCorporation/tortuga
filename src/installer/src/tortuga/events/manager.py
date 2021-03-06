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

from redis import Redis

from tortuga.config.configManager import ConfigManager
from tortuga.objectstore.manager import ObjectStoreManager
from .pubsub import EventPubSub, RedisEventPubSub
from .store import EventStore, ObjectStoreEventStore


class EventStoreManager:
    """
    Event store manager

    """
    _event_store: EventStore = None

    @classmethod
    def get(cls) -> EventStore:
        """
        Get an instance of the event store.

        :return EvemtStore:  the event store instance

        """
        if not cls._event_store:
            #
            # Events only need to exist for 24 hours
            #
            object_store = ObjectStoreManager.get('events', expire=86400)
            cls._event_store = ObjectStoreEventStore(object_store)
        return cls._event_store


class PubSubManager:
    """
    Pub/Sub service manager.

    """
    _redis_client: Redis = None
    _config_manager: ConfigManager = ConfigManager()

    @classmethod
    def get(cls) -> EventPubSub:
        """
        Get an event pubsub service instance.

        :return EventPubSub: the pub/sub service instance

        """
        if not cls._redis_client:
            cls._redis_client = Redis(
                password=cls._config_manager.getRedisPassword())
        return RedisEventPubSub(
            redis_client=cls._redis_client,
            event_store=EventStoreManager.get()
        )
