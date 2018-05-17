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

from .base import BaseEventSchema, BaseEvent


class AddNodeRequestSchema(BaseEventSchema):
    """
    Schema for the AddNodeRequest* events.

    """
    request_id = fields.String()
    request = fields.Dict()


class AddNodeRequestMixin:
    """
    Common mixin for all AddNodeRequest event classes.

    """
    schema = AddNodeRequestSchema

    def __init__(self, request_id: str, request: str, **kwargs):
        """
        Initializer.

        :param str request_id: the add node request id
        :param dict request:   the add node request
        :param kwargs:

        """
        self.request_id: str = request_id
        self.request: dict = request

        super().__init__(**kwargs)


class AddNodeRequestComplete(AddNodeRequestMixin, BaseEvent):
    """
    Event fired when new add node requests are created.

    """
    name = 'add-node-request-complete'


class AddNodeRequestQueued(AddNodeRequestMixin, BaseEvent):
    """
    Event fired when new add node requests are created.

    """
    name = 'add-node-request-queued'


class DeleteNodeRequestSchema(BaseEventSchema):
    """
    Schema for the DeleteNodeRequest* events.

    """
    request_id = fields.String()
    request = fields.Dict()


class DeleteNodeRequestMixin:
    """
    Common mixin for all DeleteNodeRequest event classes.

    """
    schema = DeleteNodeRequestSchema

    def __init__(self, request_id: str, request: dict, **kwargs):
        """
        Initializer.

        :param str request_id: the delete node request id
        :param dict request:   the node request
        :param kwargs:

        """
        self.request_id: str = request_id
        self.request: dict = request
        super().__init__(**kwargs)


class DeleteNodeRequestQueued(DeleteNodeRequestMixin, BaseEvent):
    """
    Event fired when new delete node requests are created.

    """
    name = 'delete-node-request-queued'


class DeleteNodeRequestComplete(DeleteNodeRequestMixin, BaseEvent):
    """
    Event fired when new add node requests are created.

    """
    name = 'delete-node-request-complete'
