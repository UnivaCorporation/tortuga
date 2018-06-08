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


class StringSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the StringSetting class.

    """
    default: fields.Field = fields.String()
    values: fields.Field = fields.List(fields.String())

    @post_load
    def make_instance(self, data: dict) -> 'StringSetting':
        from ..resourceadapter_settings import StringSetting
        return StringSetting(**data)


class StringSetting(BaseSetting):
    """
    A resource adapter string setting.

    """
    type: str = 'string'
    schema: BaseSettingSchema = StringSettingSchema

    def validate(self, value: str):
        if not isinstance(value, str):
            raise SettingValidationError('Value must be a string')
        super().validate(value)


