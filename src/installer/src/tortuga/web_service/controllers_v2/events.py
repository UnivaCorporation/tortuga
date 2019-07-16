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

from tortuga.events.manager import EventStoreManager
from tortuga.events.types.base import BaseEvent
from tortuga.events.types import get_event_class
from .base import Controller


class EventController(Controller):
    """
    Event web service controller class.

    """
    name = 'events'
    type_store = EventStoreManager.get()
    methods = ['GET']

    def unmarshall(self, obj_dict: dict) -> BaseEvent:
        #
        # Since different event types have different classes, we have
        # to lookup the class type before unmarshalling
        #
        event_class = get_event_class(obj_dict['name'])
        scheam_class = event_class.get_schema_class()
        unmarshalled = scheam_class().load(obj_dict)
        return event_class(**unmarshalled.data)
