from marshmallow import fields
import pytest

from tortuga.events.base import BaseEvent, BaseEventSchema
from tortuga.events.manager import EventStoreManager
from tortuga.events.store import ObjectStoreEventStore
from tortuga.objectstore.redis import RedisObjectStore


class ExampleEventSchema(BaseEventSchema):
    integer = fields.Integer()
    string = fields.Str()


class ExampleEvent(BaseEvent):
    name = 'example-event'
    schema = ExampleEventSchema

    def __init__(self, integer: int, string: str, **kwargs):
        self.integer = integer
        self.string = string
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


@pytest.fixture()
def event_store(redis):
    object_store = RedisObjectStore(namespace='events', redis_client=redis)
    store = ObjectStoreEventStore(object_store=object_store)
    #
    # Manually set the store on te store manager so that all calls to get()
    # return the same instance
    #
    EventStoreManager._event_store = store
    return store


def test_event_storage(event_store):
    #
    # Ensure that when a new event fires, it is stored it in the event store,
    # and that what we pull out again is exactly the same as what we put in
    #
    e = ExampleEvent.fire(integer=3, string='testing')
    e1 = event_store.get(e.id)
    assert e == e1
