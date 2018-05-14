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
from typing import List
import re


class MockRedis:
    def __init__(self):
        self._data_store = {}

    def delete(self, key: str):
        try:
            self._data_store.pop(key)
        except KeyError:
            pass

    def exists(self, key: str) -> bool:
        return key in self._data_store.keys()

    def hmset(self, key: str, value: dict):
        self._data_store[key] = value

    def hgetall(self, key: str) -> dict:
        return self._data_store.get(key, None)

    def keys(self, pattern: str) -> List[str]:
        keys: List[str] = []

        for k in self._data_store.keys():
            if fnmatch.fnmatch(k, pattern):
                keys.append(k)

        print('keys({}): {}'.format(pattern, keys))
        return keys

    def sadd(self, key: str, value: str):
        set_ = self._data_store.get(key, [])
        set_.append(value)
        self._data_store[key] = set_

    def smembers(self, key: str) -> List[str]:
        return self._data_store.get(key, [])

    def sort(self, key: str, by: str = None, desc: bool = False,
             alpha: bool = False) -> List[str]:
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
