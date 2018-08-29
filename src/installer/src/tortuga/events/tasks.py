# Copyright 2008-2018 Univa Corporation
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

from typing import Type

from tortuga.events.types import BaseEvent, get_event_class
from tortuga.tasks.celery import app

from .listeners import get_listnener_class, BaseListener


@app.task()
def run_event_listener(listener_name: str, event_dict: dict):
    """
    A celery task that runs the event listener for the specified event.

    :param str listener_name: the listener name
    :param dict event_dict:   the event, serialized as a dict

    """
    #
    # Load the event listener
    #
    listener_class: Type[BaseListener] = get_listnener_class(listener_name)
    listener: BaseListener = listener_class(app.app)

    #
    # Unmarshall the event
    #
    event_class = get_event_class(event_dict['name'])
    unmarshalled = event_class.schema().load(event_dict)
    event: BaseEvent = event_class(**unmarshalled.data)

    #
    # Run the event listener
    #
    listener.run_if_required(event)
