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

from typing import Dict, List, Optional, Type

from tortuga.types.application import Application
from ..exceptions import ListenerNotFoundError
from ..types import BaseEvent

#
# Dictionary, storing registered event classes
#
EVENT_LISTENERS: Dict[str, Type['BaseListener']] = {}


def get_all_listener_classes() -> List[Type['BaseListener']]:
    """
    Gets a list of all registered event listeners

    :return List[BaseListener]: a list of all event listeners

    """
    return [v for v in EVENT_LISTENERS.values()]


def get_listnener_class(name: str) -> Type['BaseListener']:
    """
    Gets the listener class for a specified listener name.

    :param str name:               the name of the listener
    :return BaseListener:          the class for the requested listener
    :raises ListenerNotFoundError: if the listener is not found

    """
    try:
        return EVENT_LISTENERS[name]
    except KeyError:
        raise ListenerNotFoundError()


class ListenerMeta(type):
    """
    Metaclass for event listeners.

    The purpose of this metaclass is to register event listeners in a so that
    they can easily be looked-up by name.

    """
    def __init__(cls: Type['BaseListener'], name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'BaseListener':
            return

        EVENT_LISTENERS[cls.name] = cls


class BaseListener(metaclass=ListenerMeta):
    """
    The base class for event listeners.

    """
    #
    # The name of the event listener, must be unique across all event
    # listeners
    #
    name: str = None

    #
    # Whether or not the listener should be run for all events
    #
    all_events: bool = False

    #
    # The event types that this listener should run for
    #
    event_types: List[Type[BaseEvent]] = []

    #
    # How long to delay (in seconds) before running this as a task
    #
    countdown: Optional[int] = None

    def __init__(self, app: Application):
        self.app = app

    @classmethod
    def should_run(cls, event: BaseEvent):
        """
        Whether or not this listener should be run for the specified event.

        :param BaseEvent event: the event to test

        :return bool: True if the listener should run, False otherwise

        """
        if cls.all_events:
            return True

        for event_type in cls.event_types:
            if isinstance(event, event_type):
                return True

            return False

    def run_if_required(self, event: BaseEvent):
        """
        Run the event listener if required.

        :param BaseEvent event: the event to respond to, if required

        """
        if self.should_run(event):
            self.run(event)

    def run(self, event: BaseEvent):
        """
        Run the listener for the specified event. Override this in your
        implementations.

        :param BaseEvent event: the event to run this listener for

        """
        pass
