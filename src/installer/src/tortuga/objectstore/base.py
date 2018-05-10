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

from typing import Optional


class ObjectStore:
    def __init__(self, namespece: str):
        """
        Initialization.

        :param str namespece: a namespace to use for these objects

        """
        self._namespace = namespece

    def get_key_name(self, key: str) -> str:
        """
        Builds the objecdt store key name to be used for storing the object.

        :param str key: the key name to use as the base

        :return str: the object store key name

        """
        return '{}:{}'.format(self._namespace, key)

    def set(self, key: str, value: dict):
        """
        Saves the object to the object store.

        :param str key:    the key name to use for the object
        :param dict value: the object to store, stores {} if None

        """
        raise NotImplementedError()

    def get(self, key: str) -> Optional[dict]:
        """
        Gets the object from the object store.

        :param str key: the key of the object to get

        :return: the object, None if not found

        """
        raise NotImplementedError()

    def delete(self, key: str):
        """
        Deletes an object from the object store.

        :param str key: the key of the object to delete

        """
        raise NotImplementedError()

    def exists(self, key: str) -> bool:
        """
        Determines whether or not a key exists.

        :param str key: the key to check for
        :return bool: True if it exists, False otherwise

        """
        raise NotImplementedError()
