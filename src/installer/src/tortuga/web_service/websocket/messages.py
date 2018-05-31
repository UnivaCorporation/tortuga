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

from typing import Type

from marshmallow import fields, Schema


class BaseMessageSchema(Schema):
    """
    The base schema for websocket messages.

    """
    type: fields.Field = fields.String(dump_only=True)
    name: fields.Field = fields.String(dump_only=True)


class BaseMessage:
    """
    The base message class. Extend for concrete implementations.

    """
    type: str = 'message'
    name: str = None
    schema: Type[BaseMessageSchema] = None


class AuthenticationRequiredMessage(BaseMessage):
    """
    Authentication required message.

    """
    name = 'authentication-required'
    schema = BaseMessageSchema


class AuthenticationFailedMessage(BaseMessage):
    """
    Authentication failed message.

    """
    name = 'authentication-failed'
    schema = BaseMessageSchema


class AuthenticationSucceededMessage(BaseMessage):
    """
    Authentication succeeded message.

    """
    name = 'authentication-succeeded'
    schema = BaseMessageSchema


class ErrorMessageSchema(BaseMessageSchema):
    """
    The schema for general error messages.

    """
    #
    # A human readable string with the reason for the error message
    #
    reason: fields.Field = fields.String()


class ErrorMessage(BaseMessage):
    """
    A general error message.

    """
    name = 'error'
    schema = ErrorMessageSchema

    def __init__(self, reason: str = None):
        """
        Initializer.

        :param str reason: the reason for the error

        """
        self.reason = reason


class SubscribeSucceededMessage(BaseMessage):
    """
    Subscription succeeded message.

    """
    name = 'subscribe-succeeded'
    schema = BaseMessageSchema


class UnsubscribeSucceededMessage(BaseMessage):
    """
    Unsubscribe succeeded message.

    """
    name = 'unsubscribe-succeeded'
    schema = BaseMessageSchema
