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

from typing import Dict, Type

from marshmallow import fields, Schema

from tortuga.events.manager import PubSubManager
from tortuga.exceptions.authenticationFailed import AuthenticationFailed
from tortuga.auth.methods import MultiAuthentionMethod
from ..auth.methods import WsUsernamePasswordAuthenticationMethod, \
    WsJwtAuthenticationMethod
from .exceptions import AuthenticationRequired, ActionNotFoundError
from .messages import AuthenticationFailedMessage, \
    AuthenticationSucceededMessage, SubscribeSucceededMessage, \
    UnsubscribeSucceededMessage
from .state import State


#
# Dictionary, storing registered action classes
#
ACTION_TYPES: Dict[str, Type['BaseAction']] = {}


def get_action_class(action: str) -> Type['BaseAction']:
    """
    Gets the action class for a specified action.

    :param str action:             the action name
    :return BaseAction:            the class for the requested action
    :raises ActionNotFoundError:   if the event class is not found

    """
    try:
        return ACTION_TYPES[action]
    except KeyError:
        raise ActionNotFoundError()


class ActionMeta(type):
    """
    Metaclass for action types.

    The purpose of this metaclass is to register action types in a so that
    they can easily be looked-up by name.

    """
    def __init__(cls: 'BaseAction', name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'BaseAction':
            return

        ACTION_TYPES[cls.action] = cls


class BaseActionSchema(Schema):
    """
    The base schema for websocket actions.

    """
    action = fields.String(dump_only=True)


class BaseAction(metaclass=ActionMeta):
    """
    The base websocket action. Extend for concrete actions.

    """
    action = None
    schema = None

    def __init__(self, state: State):
        """
        Initializer.

        :param State state: the current websocket state instance

        """
        self._state: State = state

    def do(self):
        """
        This method is called if this action is requested via the websocket.

        """
        raise NotImplementedError()


class AuthenticateActionSchema(BaseActionSchema):
    """
    Schema for the authenticate action.

    """
    #
    # The authentication method to use
    #
    method = fields.String()

    #
    # The data required for the specified authentication method. See
    # tortuga.web_service.auth.methods.Ws* for details on the various
    # authentication methods and what they expect here.
    #
    data = fields.Dict()


class AuthenticateAction(BaseAction):
    """
    The authentication action.

    """
    action = 'authenticate'
    schema = AuthenticateActionSchema

    #
    # List of currently supported authentication methods.
    #
    _authenticator = MultiAuthentionMethod([
        WsUsernamePasswordAuthenticationMethod(),
        WsJwtAuthenticationMethod()
    ])

    def __init__(self, method: str, data: dict, state: State):
        """
        Initializer.

        :param str method: the authentication method for this action
        :param data:       the data required for this authentication action
        :param state:      the current websocket state instance

        """
        super().__init__(state)
        self.method = method
        self.data = data

    def do(self):
        """
        See superclass.

        """
        #
        # Attempt to authenticate the user using one of the authentication
        # methods. If authentication succeeds, we do the following:
        #
        # - set the authentication state as true
        # - set the username for the current websocket state
        # - clear out any authentication timeouts
        # - enqueue an authentication successful message
        #
        try:
            username = self._authenticator.authenticate(action=self)
            self._state.authenticated = True
            self._state.username = username
            self._state.clear_authentication_timeout()
            self._state.enqueue_message(AuthenticationSucceededMessage())

        #
        # If the authentication failed, then we need to do some housekeeping:
        #
        # - set the authentication state as false
        # - nullify the username for the current websocket state
        # - enqueue an authentication failed message
        #
        except AuthenticationFailed:
            self._state.authenticated = False
            self._state.username = None
            self._state.enqueue_message(AuthenticationFailedMessage())


class SubscribeAction(BaseAction):
    """
    The subscribe action. The purpose of this action is to subscribe
    the user to the events pubsub.

    """
    action = 'subscribe'
    schema = BaseActionSchema

    def do(self):
        """
        See superclass.

        """
        #
        # You cannot subscribe without being authenticated
        #
        if not self._state.authenticated:
            raise AuthenticationRequired()

        #
        # Don't re-subscribe if they are already subscribed
        #
        if not self._state.pubsub:
            self._state.pubsub = PubSubManager.get()
            self._state.pubsub.subscribe()

        #
        # Enqueue a subscription success message
        #
        self._state.enqueue_message(SubscribeSucceededMessage())


class UnsubscribeAction(BaseAction):
    """
    The unsubscribe action. The purpose of this action is to unsubscribe
    the user from the events pubsub.

    """
    action = 'unsubscribe'
    schema = BaseActionSchema

    def do(self):
        """
        See superclass.

        """
        #
        # You cannot do anything with subscriptions unless the user is
        # authenticated
        #
        if not self._state.authenticated:
            raise AuthenticationRequired()

        #
        # Don't bother unsubcribing them if they currently don't have a
        # subscription
        #
        if self._state.pubsub:
            self._state.pubsub.unsubscribe()
            self._state.pubsub = None

        #
        # Enqueue a unsubscribe success message
        #
        self._state.enqueue_message(UnsubscribeSucceededMessage())
