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


class CloudServerActionCreatedSchema(BaseEventSchema):
    """
    Schema for the CloudServerActionCreated events.

    """
    cloudserveraction_id = fields.String()


class CloudServerActionCreated(BaseEvent):
    schema_class = CloudServerActionCreatedSchema

    name = 'cloud-server-action-created'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloudserveraction_id: str = kwargs.get('cloudserveraction_id',
                                                    None)


class CloudServerActionUpdatedSchema(BaseEventSchema):
    """
    Schema for CloudServerActionUpdated events.

    """
    cloudserveraction_id = fields.String()
    previous_cloudserveraction = fields.Dict()


class CloudServerActionUpdated(BaseEvent):
    schema_class = CloudServerActionUpdatedSchema

    name = 'cloud-server-action-updated'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloudserveraction_id: str = kwargs.get('cloudserveraction_id',
                                                    None)
        self.previous_cloudserveraction: dict = kwargs.get(
            'previous_cloudserveraction', {})


class CloudServerActionDeletedSchema(BaseEventSchema):
    """
    Schema for CloudServerActionDeleted events.

    """
    cloudserveraction_id = fields.String()
    previous_cloudserveraction = fields.Dict()


class CloudServerActionDeleted(BaseEvent):
    schema_class = CloudServerActionDeletedSchema

    name = 'cloud-server-action-deleted'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloudserveraction_id: str = kwargs.get('cloudserveraction_id',
                                                    None)
        self.previous_cloudserveraction: dict = kwargs.get(
            'previous_cloudserveraction', {})
