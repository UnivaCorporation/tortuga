from typing import Iterator, Optional

from .base import BaseEvent, get_event_class
from tortuga.objectstore.base import ObjectStore


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

    def list(self) -> Iterator[BaseEvent]:
        """
        Gets a iterator of events from the event store.

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

    def list(self) -> Iterator[BaseEvent]:
        """
        See superclass.

        :return Iterator[BaseEvent]:

        """
        for _, event_dict in self._store.list():
            yield self._unmarshall(event_dict)
