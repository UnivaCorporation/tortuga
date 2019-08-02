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

import logging
from typing import Iterator, Optional
import uuid

from tortuga.events.types import (ResourceRequestCreated,
                                  ResourceRequestUpdated,
                                  ResourceRequestDeleted)
from tortuga.logging import EVENTS_NAMESPACE
from tortuga.typestore.objectstore import ObjectStoreTypeStore
from .types import BaseResourceRequest
from .types import get_resource_request_class


logger = logging.getLogger(EVENTS_NAMESPACE)


class ResourceRequestStore:
    """
    Base class for the resource_request storage back-end.

    """
    def save(self, resource_request: BaseResourceRequest) -> BaseResourceRequest:
        """
        Saves the resource_request to the resource_request store.

        :param BaseResourceRequest resource_request: the resource_request to
                                   save

        """
        raise NotImplementedError()

    def get(self, resource_request_id: str) -> Optional[BaseResourceRequest]:
        """
        Gets an resource_request from the resource_request store.

        :param str resource_request_id: the id of the resource_request to
                                        retrieve

        :return: the resource_request instance, if found, otherwise None

        """
        raise NotImplementedError()

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[BaseResourceRequest]:
        """
        Gets a iterator of resource_requests from the resource_request store.

        :param str order_by:     the name of the object attribute to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)
        :param int limit:        the number of objects to limit in the
                                 iterator
        :param filters:          one or more filters to apply to the list

        :return: an iterator of resource_requests

        """
        raise NotImplementedError()


class ObjectStoreResourceRequestStore(ObjectStoreTypeStore,
                                      ResourceRequestStore):
    type_class = BaseResourceRequest

    def save(self, resource_request: BaseResourceRequest) -> BaseResourceRequest:
        rr_old: Optional[BaseResourceRequest] = None
        if resource_request.id:
            rr_old = self.get(resource_request.id)
        else:
            resource_request.id = str(uuid.uuid4())

        rr = super().save(resource_request)
        self._fire_events(rr_old, rr)

        return resource_request

    def _fire_events(self, rr_old: Optional[BaseResourceRequest],
                     rr: BaseResourceRequest):
        if rr_old:
            self._event_updated(rr_old, rr)
        else:
            self._event_created(rr)

    def _event_updated(self, rr_old: Optional[BaseResourceRequest],
                       rr: BaseResourceRequest):
        data = self.marshall(rr)
        previous_data = self.marshall(rr_old)

        if data != previous_data:
            ResourceRequestUpdated.fire(
                resourcerequest_id=rr.id,
                previous_resourcerequest=previous_data
            )

    def _event_created(self, rr: BaseResourceRequest):
        ResourceRequestCreated.fire(resourcerequest_id=rr.id)

    def delete(self, obj_id: str):
        rr_old = self.get(obj_id)
        if not rr_old:
            return

        super().delete(obj_id)

        ResourceRequestDeleted.fire(
            resourcerequest_id=rr_old.id,
            previous_resourcerequest=self.marshall(rr_old)
        )

    def marshall(self, obj: BaseResourceRequest) -> dict:
        schema_class = obj.get_schema_class()
        marshalled = schema_class().dump(obj)
        return marshalled.data

    def unmarshall(self, obj_dict: dict) -> BaseResourceRequest:
        resource_request_class = get_resource_request_class(
            obj_dict['resource_type'])
        schema_class = resource_request_class.get_schema_class()
        unmarshalled = schema_class().load(obj_dict)
        return resource_request_class(**unmarshalled.data)
