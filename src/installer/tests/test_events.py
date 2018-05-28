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

from marshmallow import fields
import pytest

from tortuga.events.types.base import BaseEvent, BaseEventSchema
from tortuga.events.manager import EventStoreManager, PubSubManager
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
    #
    # Manually set the redis instance on the pub/sub manager so that it
    # is there for any internal calls to the manager
    #
    PubSubManager._redis_client = redis
    return store


def test_event_storage(event_store):
    #
    # Ensure that when a new event fires, it is stored it in the event store,
    # and that what we pull out again is exactly the same as what we put in
    #
    e = ExampleEvent.fire(integer=3, string='testing')
    e1 = event_store.get(e.id)
    assert e == e1


def test_event_list(event_store):
    #
    # Ensure that when a multiple events fire, that the same events are
    # retrieved via the event store's list method
    #
    events_in = [
        ExampleEvent.fire(integer=3, string='testing'),
        ExampleEvent.fire(integer=4, string='testing2'),
        ExampleEvent.fire(integer=5, string='abc123')
    ]

    for evt_out in event_store.list():
        for evt_in in events_in:
            if evt_in == evt_out:
                events_in.remove(evt_in)
                break
    assert events_in == []


def test_event_list_filter(event_store):
    ExampleEvent.fire(integer=3, string='testing')
    ExampleEvent.fire(integer=4, string='testing2')
    ExampleEvent.fire(integer=5, string='abc123')

    #
    # Ensure that events can be filtered and sorted
    #
    integers = []
    for evt in event_store.list(order_by='integer', order_desc=True,
                                integer__gt=3):
        integers.append(evt.integer)
    assert integers == [5, 4]


def test_event_pubsub(event_store):
    pubsub = PubSubManager.get()
    pubsub.subscribe()

    events = [
        ExampleEvent.fire(integer=3, string='testing'),
        ExampleEvent.fire(integer=4, string='testing2'),
        ExampleEvent.fire(integer=5, string='abc123')
    ]

    #
    # Assert that the subscription gets the events back in order
    #
    for evt in events:
        evt_sub = pubsub.get_message()
        print(evt_sub)
        assert evt == evt_sub
