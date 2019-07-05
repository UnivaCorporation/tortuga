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

from tortuga.logging import EVENTS_NAMESPACE
from tortuga.typestore.objectstore import ObjectStoreTypeStore
from .types import BaseEvent
from .types import get_event_class


logger = logging.getLogger(EVENTS_NAMESPACE)


class EventStore:
    """
    Base class for the event storage back-end.

    """
    def save(self, event: BaseEvent):
        """
        Saves the event to the event store.

        :param BaseEvent event: the event to save

        """
        raise NotImplementedError()

    def get(self, event_id: str) -> Optional[BaseEvent]:
        """
        Gets an event from the event store.

        :param str event_id: the id of the event to retrieve

        :return: the event instance, if found, otherwise None

        """
        raise NotImplementedError()

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[BaseEvent]:
        """
        Gets a iterator of events from the event store.

        :param str order_by:     the name of the object attribute to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)
        :param int limit:        the number of objects to limit in the
                                 iterator
        :param filters:          one or more filters to apply to the list

        :return: an iterator of events

        """
        raise NotImplementedError()


class ObjectStoreEventStore(ObjectStoreTypeStore):
    type_class = BaseEvent

    def unmarshall(self, obj_dict: dict) -> BaseEvent:
        #
        # Since different event types have different classes, we have
        # to lookup the class type before unmarshalling
        #
        event_class = get_event_class(obj_dict['name'])
        unmarshalled = event_class.schema().load(obj_dict)
        return event_class(**unmarshalled.data)
