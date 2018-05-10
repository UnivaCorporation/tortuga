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

import json
from logging import getLogger
from typing import Optional

from .base import ObjectStore


logger = getLogger(__name__)


class RedisObjectStore(ObjectStore):
    """
    An implementation of the ObjectStore that stores objects in an Redis
    KV store.

    """
    def __init__(self, namespace: str, redis_client):
        """
        Initialization.

        :param str namespace:      the namespace to use for storing objects
        :param Redis redis_client: the (initialized) redis client to use

        """
        super().__init__(namespace)
        self._redis = redis_client

    def set(self, key: str, value: dict):
        """
        See superclass.

        :param key:
        :param value:

        """
        if not value:
            value = {}

        logger.debug('set: {} -> {}'.format(key, value))

        #
        # If any of the keys are more complex data structures, store them
        # as serialized JSON
        #
        to_store = {}
        for k, v in value.items():
            if isinstance(v, (dict, list, tuple)):
                to_store[k] = 'JSON:{}'.format(json.dumps(v))
            else:
                to_store[k] = v

        self._redis.hmset(self.get_key_name(key), to_store)

    def get(self, key: str) -> Optional[dict]:
        """
        See superclass.

        :param key:

        :return:

        """
        result = self._redis.hgetall(self.get_key_name(key))

        if not result:
            return None

        #
        # Deserialize any values that were serialized as JSON
        #
        to_return = {}
        for k, v in result.items():
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            if isinstance(v, str) and v.startswith('JSON:'):
                to_return[k] = json.loads(v[5:])
            else:
                to_return[k] = v

        logger.debug('get: {} -> {}'.format(key, to_return))

        return to_return

    def delete(self, key: str):
        """
        See superclass.

        :param key:

        """
        logger.debug('delete: {}'.format(key))
        self._redis.delete(self.get_key_name(key))

    def exists(self, key: str) -> bool:
        """
        See superclass.

        :param key:

        """
        result = self._redis.exists(self.get_key_name(key))
        logger.debug('get: {} -> {}'.format(key, result))
        return result
