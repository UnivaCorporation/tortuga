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
    listener: BaseListener = listener_class()

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
