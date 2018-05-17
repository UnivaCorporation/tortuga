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


class AddNodeRequestQueuedSchema(BaseEventSchema):
    """
    Schema for the AddNodeRequestQueued event.

    """
    request_id = fields.String()


class AddNodeRequestQueued(BaseEvent):
    """
    Event fired when new add node requests are created.

    """
    name = 'add-node-request-queued'
    schema = AddNodeRequestQueuedSchema

    def __init__(self, request_id: str, **kwargs):
        """
        Initializer.

        :param str request_id: the add node request id
        :param kwargs:

        """
        self.request_id: str = request_id
        super().__init__(**kwargs)


class DeleteNodeRequestQueuedSchema(BaseEventSchema):
    """
    Schema for the DeleteNodeRequestQueued event.

    """
    transaction_id = fields.String()


class DeleteNodeRequestQueued(BaseEvent):
    """
    Event fired when new delete node requests are created.

    """
    name = 'delete-node-request-queued'
    schema = DeleteNodeRequestQueuedSchema

    def __init__(self, transaction_id: str, **kwargs):
        """
        Initializer.

        :param str transaction_id: the delete node request transaction id
        :param kwargs:

        """
        self.transaction_id: str = transaction_id
        super().__init__(**kwargs)
