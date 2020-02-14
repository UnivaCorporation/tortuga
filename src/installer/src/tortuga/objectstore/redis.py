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
import logging
from typing import Iterator, Optional, Tuple

from redis.exceptions import ResponseError

from tortuga.logging import OBJECT_STORE_NAMESPACE
from .base import ObjectStore

logger = logging.getLogger(OBJECT_STORE_NAMESPACE)


class RedisObjectStore(ObjectStore):
    """
    An implementation of the ObjectStore that stores objects in an Redis
    KV store.

    """
    #
    # A list of reserved keys, that are required for internal use
    #
    RESERVED_KEYS = ['INDEX']

    def __init__(self, namespace: str, redis_client, expire: int = 0):
        """
        Initialization.

        :param str namespace:      the namespace to use for storing objects
        :param Redis redis_client: the (initialized) redis client to use
        :param int expire:         objects should expire after x seconds

        """
        super().__init__(namespace, expire)
        self._redis = redis_client

    def _get_index_key_name(self) -> str:
        """
        Gets the key name for the Redis index set.

        :return str: the key name

        """
        return self.get_key_name('INDEX')

    def set(self, key: str, value: dict):
        """
        See superclass.

        :param key:
        :param value:

        """
        if key in self.RESERVED_KEYS:
            raise Exception('Key reserved for internal use: {}'.format(key))

        if not value:
            value = {}

        logger.debug('set({}, {})'.format(key, value))

        #
        # If any of the keys are more complex data structures, store them
        # as serialized JSON
        #
        to_store = {}
        for k, v in value.items():
            if isinstance(v, (dict, list, tuple)):
                to_store[k] = 'JSON:{}'.format(json.dumps(v))
            elif v is None:
                to_store[k] = 'NULL'
            else:
                to_store[k] = v

        key = self.get_key_name(key)
        self._redis.hmset(key, to_store)
        if self._expire:
            self._redis.expire(key, self._expire)

        #
        # Create a Redis set for the purposes of indexing, sorting, etc.
        #
        self._redis.sadd(self._get_index_key_name(), key)

    def get(self, key: str) -> Optional[dict]:
        """
        See superclass.

        :param key:

        :return Optional[dict]:

        """
        return self._get(self.get_key_name(key))

    def _get(self, key: str) -> Optional[dict]:
        """
        This is the same as the get() method, except it expects the key
        prefix to already prepended to the key.

        :param key: the key, namespace prefixed

        :return: the object, if found, None otherwise

        """
        result = self._redis.hgetall(key)

        if not result:
            return None

        logger.debug('get({}) -> {}'.format(key, result))
        return self._deserialize(result)

    def _deserialize(self, hsh: dict) -> dict:
        """
        Reconstitutes a Redis hash.

        :param dict hsh: the Redis hash to deserialize

        :return dict: the deserialized result

        """
        deserialized = {}
        for k, v in hsh.items():
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            if isinstance(v, str) and v.startswith('JSON:'):
                deserialized[k] = json.loads(v[5:])
            elif v == 'NULL':
                deserialized[k] = None
            else:
                deserialized[k] = v

        return deserialized

    def list_sorted(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False) -> Iterator[Tuple[str, dict]]:
        """
        See superclass.

        :param str order_by:
        :param bool order_desc:
        :param bool order_alpha:

        :return Iterator[dict]:

        """
        #
        # Un-ordered list
        #
        if not order_by:
            for key in self._redis.smembers(self._get_index_key_name()):
                key = key.decode()
                yield (self._remove_namespace(key), self._get(key))

            return

        #
        # Ordered list
        #
        try:
            sort_by = '*->{}'.format(order_by)
            for key in self._redis.sort(self._get_index_key_name(),
                                        by=sort_by, desc=order_desc,
                                        alpha=order_alpha):
                key = key.decode()
                yield (self._remove_namespace(key), self._get(key))

            return

        except ResponseError as e:
            #
            # This error means that Redis can't sort this attribute
            # as a double, which is it's default behavior. We need to
            # specify order_alpha instead
            #
            if str(e) == "One or more scores can't be converted into double":
                raise Exception(
                    '{} must be sorted using order_alpha'.format(order_by)
                )
            else:
                raise

    def _remove_namespace(self, key: str) -> str:
        """
        Removes the namespace prefix from a key.

        :param str key: the key from which the namespace prefix will be
                        removed

        :return str: the key without the namespace prefix

        """
        return key.replace('{}:'.format(self._namespace), '')

    def delete(self, key: str):
        """
        See superclass.

        :param key:

        """
        logger.debug('delete({})'.format(key))
        key = self.get_key_name(key)
        #
        # Remove from the Redis set
        #
        self._redis.srem(self._get_index_key_name(), key)
        #
        # Delete the object
        #
        self._redis.delete(key)

    def exists(self, key: str) -> bool:
        """
        See superclass.

        :param key:

        """
        result = self._redis.exists(self.get_key_name(key))
        logger.debug('exists({}) -> {}'.format(key, result))
        return result
