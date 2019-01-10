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
from tortuga.objectstore.base import matches_filters, ObjectStore
from .types import BaseEvent, get_event_class


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


class ObjectStoreEventStore(EventStore):
    """
    An implementation of the event store that saves data in the Tortuga
    object store.
    
    """
    def __init__(self, object_store: ObjectStore):
        self._store = object_store

    def save(self, event: BaseEvent):
        """
        See superclass.

        :param BaseEvent event:

        """
        marshalled = event.schema().dump(event)
        event_dict = marshalled.data
        self._store.set(event.id, event_dict)

    def get(self, event_id: str) -> Optional[BaseEvent]:
        """
        See superclass.

        :param str event_id:

        :return BaseEvent:

        """
        event_dict = self._store.get(event_id)
        if event_dict is None:
            return None
        return self._unmarshall(event_dict)

    def _unmarshall(self, event_dict: dict) -> BaseEvent:
        """
        Unmarshalls an event dict into an event class instance.

        :param dict event_dict:
        :return BaseEvent: the unmarshalled base event

        """
        event_class = get_event_class(event_dict['name'])
        unmarshalled = event_class.schema().load(event_dict)
        return event_class(**unmarshalled.data)

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[BaseEvent]:
        """
        See superclass.

        :return Iterator[BaseEvent]:

        """
        logger.debug(
            'list(order_by={}, order_desc={}, limit, filters={}) -> ...'.format(
                order_by, order_desc, limit, filters
            )
        )

        count = 0
        for _, event_dict in self._store.list_sorted(order_by=order_by,
                                                     order_desc=order_desc,
                                                     order_alpha=order_alpha):
            obj = self._unmarshall(event_dict)
            if matches_filters(obj, filters):
                count += 1
                if limit and count == limit:
                    yield obj
                    return

                yield obj
