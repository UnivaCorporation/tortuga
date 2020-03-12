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

from typing import Optional

from marshmallow import fields

from .base import BaseResourceRequest, BaseResourceRequestSchema


class ScaleSetResourceRequestSchema(BaseResourceRequestSchema):
    hardwareprofile_name = fields.String()
    softwareprofile_name = fields.String()
    resourceadapter_name = fields.String()
    resourceadapter_profile_name = fields.String()
    min_nodes = fields.Integer()
    max_nodes = fields.Integer()
    desired_nodes = fields.Integer()
    instance_template_name = fields.String()


class ScaleSetResourceRequest(BaseResourceRequest):
    schema_class = ScaleSetResourceRequestSchema
    resource_type = 'scale-set'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hardwareprofile_name: Optional[str] = kwargs.get('hardwareprofile_name', None)
        self.softwareprofile_name: Optional[str] = kwargs.get('softwareprofile_name', None)
        self.resourceadapter_name: Optional[str] = kwargs.get('resourceadapter_name', None)
        self.resourceadapter_profile_name: Optional[str] = kwargs.get('resourceadapter_profile_name', None)
        self.min_nodes: int = kwargs.get('min_nodes', 0)
        self.max_nodes: int = kwargs.get('max_nodes', 0)
        self.desired_nodes: int = kwargs.get('desired_nodes', 0)
        self.instance_template_name: Optional[str] = \
            kwargs.get('instance_template_name', None)
