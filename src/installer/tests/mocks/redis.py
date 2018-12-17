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

import fnmatch
from typing import Dict, List, Union
import re


class MockRedis:
    def __init__(self, *args, **kwargs):
        self._data_store: Dict[bytes, Union[bytes, dict]] = {}
        self._channels: List[bytes] = []
        self._pubsubs: List[PubSub] = []

    def delete(self, key: str):
        bkey = key.encode()

        try:
            self._data_store.pop(bkey)
        except KeyError:
            pass

    def exists(self, key: str) -> bool:
        bkey = key.encode()

        return bkey in self._data_store.keys()

    def hmset(self, key: str, value: dict):
        bkey = key.encode()

        self._data_store[bkey] = value

    def hgetall(self, key: str) -> dict:
        bkey = key.encode()

        return self._data_store.get(bkey, None)

    def keys(self, pattern: str) -> List[bytes]:
        keys: List[bytes] = []

        for bk in self._data_store.keys():
            k = bk.decode()
            if fnmatch.fnmatch(k, pattern):
                keys.append(bk)

        return keys

    def publish(self, channel: str, value: str):
        bchannel = channel.encode()
        bvalue = value.encode()

        if bchannel not in self._channels:
            self._channels.append(bchannel)
            for pubsub in self._pubsubs:
                pubsub._new_channel()

        for pubsub in self._pubsubs:
            pubsub._new_message(bchannel, bvalue)

    def pubsub(self) -> 'PubSub':
        p = PubSub(self)
        self._pubsubs.append(p)

        return p

    def sadd(self, key: str, value: str):
        bkey = key.encode()

        set_ = self._data_store.get(bkey, [])
        set_.append(value.encode())
        self._data_store[bkey] = set_

    def smembers(self, key: str) -> List[bytes]:
        bkey = key.encode()

        return self._data_store.get(bkey, [])

    def sort(self, key: str, by: str = None, desc: bool = False,
             alpha: bool = False) -> List[bytes]:
        result = self.smembers(key)

        sort_key = None
        if by:
            m = re.match('\*->(.+)', by)
            groups = m.groups()
            if not len(groups) == 1:
                raise Exception('Mock does not support by: {}'.format(by))
            sort_key = lambda obj_key: self._data_store[obj_key][groups[0]]

        result.sort(key=sort_key)

        if desc:
            result.reverse()

        return result


class PubSub:
    def __init__(self, redis_client: MockRedis):
        self._redis: MockRedis = redis_client
        self._patterns: List[bytes] = []
        self._subscriptions: List[bytes] = []
        self._messages: List[dict] = []

    def get_message(self, ignore_subscribe_messages: bool = True):
        try:
            return self._messages.pop()

        except IndexError:
            return None

    def psubscribe(self, pattern: str):
        bpattern = pattern.encode()

        if bpattern not in self._patterns:
            self._patterns.append(bpattern)

        for bc in self._redis._channels:
            c = bc.decode()
            if fnmatch.fnmatch(c, pattern):
                self.subscribe(c)

    def subscribe(self, channel: str):
        bchannel = channel.encode()

        if bchannel in self._subscriptions:
            return
        self._subscriptions.append(bchannel)

    def unsubscribe(self):
        self._patterns = []
        self._subscriptions = []
        self._messages = []

    def _new_channel(self):
        """
        Callback for when new channels are added to redis.

        """
        for bp in self._patterns:
            p = bp.decode()
            self.psubscribe(p)

    def _new_message(self, channel: bytes, message: bytes):
        """
        Callback for when a new message appears in the channel.

        :param channel: the channel the new message appeared on
        :param message: the message

        """
        if channel not in self._subscriptions:
            return

        msg = {
            'data': message
        }
        self._messages.insert(0, msg)

