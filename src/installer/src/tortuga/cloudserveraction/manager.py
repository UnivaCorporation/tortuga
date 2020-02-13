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

from tortuga.objectstore.manager import ObjectStoreManager
from .store import CloudServerActionStore, ObjectStoreCloudServerActionStore


class CloudServerActionStoreManager:
    """
    CloudServerAction store manager

    """
    _cloudserver_action_store: CloudServerActionStore = None

    @classmethod
    def get(cls) -> CloudServerActionStore:
        """
        Get an instance of the cloudserver action store.

        :return CloudServerActionStore: the cloudserver action store instance

        """
        if not cls._cloudserver_action_store:
            object_store = ObjectStoreManager.get('cloudserveractions')
            cls._cloudserver_action_store = ObjectStoreCloudServerActionStore(
                object_store)
        return cls._cloudserver_action_store
