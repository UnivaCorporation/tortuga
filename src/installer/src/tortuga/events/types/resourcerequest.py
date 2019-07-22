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


class ResourceRequestCreatedSchema(BaseEventSchema):
    """
    Schema for the ResourceRequestCreated events.

    """
    resourcerequest_id = fields.String()


class ResourceRequestCreated(BaseEvent):
    schema_class = ResourceRequestCreatedSchema

    name = 'resource-request-created'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resourcerequest_id: str = kwargs.get('resourcerequest_id', None)


class ResourceRequestUpdatedSchema(BaseEventSchema):
    """
    Schema for ResourceRequestUpdated events.

    """
    resourcerequest_id = fields.String()
    previous_resourcerequest = fields.Dict()


class ResourceRequestUpdated(BaseEvent):
    schema_class = ResourceRequestUpdatedSchema

    name = 'resource-request-updated'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resourcerequest_id: str = kwargs.get('resourcerequest_id', None)
        self.previous_resourcerequest: dict = kwargs.get('previous_resourcerequest', {})


class ResourceRequestDeletedSchema(BaseEventSchema):
    """
    Schema for ResourceRequestDeleted events.

    """
    resourcerequest_id = fields.String()
    previous_resourcerequest = fields.Dict()


class ResourceRequestDeleted(BaseEvent):
    schema_class = ResourceRequestDeletedSchema

    name = 'resource-request-deleted'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resourcerequest_id: str = kwargs.get('resourcerequest_id', None)
        self.previous_resourcerequest: dict = kwargs.get('previous_resourcerequest', {})
