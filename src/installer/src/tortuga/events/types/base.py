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
from typing import Dict, Type
import uuid

from marshmallow import Schema, fields

from ..exceptions import EventNotFoundError


#
# Dictionary, storing registered event classes
#
EVENT_TYPES: Dict[str, Type['BaseEvent']] = {}


def get_event_class(name: str) -> Type['BaseEvent']:
    """
    Gets the event class for a specified event name.

    :param str name:              the name of the event
    :return BaseEvent:            the class for the requested event
    :raises EventNotFoundError:   if the event class is not found

    """
    try:
        return EVENT_TYPES[name]
    except KeyError:
        raise EventNotFoundError()


class EventMeta(type):
    """
    Metaclass for event types.

    The purpose of this metaclass is to register event types in a so that they
    can easily be looked-up by name.

    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'BaseEvent':
            return

        EVENT_TYPES[cls.name] = cls


class BaseEventSchema(Schema):
    """
    Marshmallow schema for events.

    """
    name: fields.Field = fields.String(dump_only=True)
    id: fields.Field = fields.String()
    timestamp: fields.Field = fields.DateTime()
    message: fields.Field = fields.String(required=False)


class BaseEvent(metaclass=EventMeta):
    """
    This is the base event type. This class is meant to be overridden to
    implement specific event types.

    """
    #
    # A name for the event type
    #
    name: str = None
    #
    # A marshmallow schema for the event
    #
    schema: Type[BaseEventSchema] = None

    def __init__(self, message=None, **kwargs):
        """
        Initialization.

        :param kwargs: any arguments provided will be assigned as attributes
                       directly on the instance.

        """
        self.id: str = None
        self.timestamp: datetime.datetime = None
        self.message = message

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def fire(cls, **kwargs) -> 'BaseEvent':
        """
        Fires an event. The act of firing an event does the following:

        - A new event instance is created
        - A new id is generated for the event
        - A new timestamp is generated for the event
        - The event is stored in the event store
        - The event is published to a pubsub channel
        - Any matching event listeners are run

        :param kwargs: Arguments passed here will be passed to the
                       events class initialization (__init__) method

        :return: the new event instance

        """
        event = cls(**kwargs)
        event.id = str(uuid.uuid4())
        event.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

        cls._store_event(event)
        cls._publish_event(event)
        cls._schedule_event_listeners(event)

        return event

    @classmethod
    def _store_event(cls, event: 'BaseEvent'):
        """
        Stores the event in the event store.

        :param BaseEvent event:

        """
        from ..manager import EventStoreManager

        store = EventStoreManager.get()
        store.save(event)

    @classmethod
    def _publish_event(cls, event: 'BaseEvent'):
        """
        Publishes the even to the pubsub.

        :param BaseEvent event:

        """
        from ..manager import PubSubManager

        pubsub = PubSubManager.get()
        pubsub.publish(event)

    @classmethod
    def _schedule_event_listeners(cls, event: 'BaseEvent'):
        """
        Schedules all event listeners to run, as required.

        :param BaseEvent event:

        """
        from ..listeners import get_all_listener_classes
        from ..tasks import run_event_listener

        event_dict = event.schema().dump(event).data
        for listener_class in get_all_listener_classes():
            if listener_class.should_run(event):
                kwargs = {}
                if listener_class.countdown is not None:
                    kwargs['countdown'] = listener_class.countdown
                run_event_listener.apply_async(
                    args=[listener_class.name, event_dict],
                    **kwargs
                )
