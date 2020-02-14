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

import datetime
import logging
from typing import Iterator, Optional
import uuid

from tortuga.events.types import (CloudServerActionCreated,
                                  CloudServerActionUpdated,
                                  CloudServerActionDeleted)
from tortuga.logging import NODE_NAMESPACE
from tortuga.typestore.objectstore import ObjectStoreTypeStore
from .types import CloudServerAction

logger = logging.getLogger(NODE_NAMESPACE)


class CloudServerActionStore:
    """
    Base class for the cloud server action storage back-end.

    """

    def save(self, csa: CloudServerAction) -> CloudServerAction:
        """
        Saves the cloud server action to the store.

        :param CloudServerAction csa: the cloud server action 
                                                     to save

        """
        raise NotImplementedError()

    def get(self, csa_id: str) -> Optional[CloudServerAction]:
        """
        Gets an cloudserver action from the cloudserver action store.

        :param str csa_id: the id of the cloud server action
                                          to retrieve

        :return: the cloud server action instance, if found, otherwise None

        """
        raise NotImplementedError()

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[CloudServerAction]:
        """
        Gets a iterator of clouds erver actions from the cloud server action 
        store.

        :param str order_by:     the name of the object attribute to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)
        :param int limit:        the number of objects to limit in the
                                 iterator
        :param filters:          one or more filters to apply to the list

        :return: an iterator of cloud server actions

        """
        raise NotImplementedError()


class ObjectStoreCloudServerActionStore(ObjectStoreTypeStore,
                                        CloudServerActionStore):
    type_class = CloudServerAction

    def save(self, csa: CloudServerAction) -> CloudServerAction:
        csa_old: Optional[CloudServerAction] = None
        if csa.id:
            csa_old = self.get(csa.id)
        else:
            csa.id = str(uuid.uuid4())
            if not csa.status:
                csa.stats = CloudServerAction.STATUS_CREATED
            csa.timestamp = datetime.datetime.now()

        csa = super().save(csa)
        self._fire_events(csa_old, csa)

        return csa

    def _fire_events(self, csa_old: Optional[CloudServerAction],
                     csa: CloudServerAction):
        if csa_old:
            self._event_updated(csa_old, csa)
        else:
            self._event_created(csa)

    def _event_updated(self, csa_old: Optional[CloudServerAction],
                       csa: CloudServerAction):
        data = self.marshall(csa)
        previous_data = self.marshall(csa_old)

        if data != previous_data:
            CloudServerActionUpdated.fire(
                cloudserveraction_id=csa.id,
                previous_cloudserveraction=previous_data
            )

    def _event_created(self, csa: CloudServerAction):
        CloudServerActionCreated.fire(cloudserveraction_id=csa.id)

    def delete(self, obj_id: str):
        csa_old = self.get(obj_id)
        if not csa_old:
            return

        super().delete(obj_id)

        CloudServerActionDeleted.fire(
            cloudserveraction_id=csa_old.id,
            previous_cloudserveraction=self.marshall(csa_old)
        )
