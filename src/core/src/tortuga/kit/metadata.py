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

from typing import List

from marshmallow import Schema, fields

from tortuga.config import VERSION


KIT_METADATA_FILE = 'kit.json'


class KitMetadataSchema(Schema):
    """
    Schema for the kit meta data.

    """
    name: str = fields.String(required=True)
    version: str = fields.String(required=True)
    iteration: str = fields.String(required=True)
    description: str = fields.String(required=False)
    requires_core: str = fields.String(default=VERSION)
    include_files: List[str] = fields.List(fields.String(), required=False)
    exclude_files: List[str] = fields.List(fields.String(), required=False)
