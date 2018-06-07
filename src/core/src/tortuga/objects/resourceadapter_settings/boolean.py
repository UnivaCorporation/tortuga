#
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

from marshmallow import fields, post_load

from .base import BaseSetting, BaseSettingSchema
from .exceptions import SettingValidationError


class BooleanSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the BooleanSetting class.

    """
    default: fields.Field = fields.Boolean()

    @post_load
    def make_instance(self, data: dict) -> 'BooleanSetting':
        return BooleanSetting(**data)


class BooleanSetting(BaseSetting):
    """
    Boolean resource adapter setting.

    """
    type: str = 'boolean'
    schema: BaseSetting = BooleanSettingSchema

    def validate(self, value: bool):
        if not isinstance(value, bool):
            raise SettingValidationError('Value must be an boolean')
        super().validate(value)


