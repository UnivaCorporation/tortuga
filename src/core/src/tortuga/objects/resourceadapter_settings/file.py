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

import os.path

from marshmallow import fields, post_load

from .base import BaseSettingSchema
from .exceptions import SettingValidationError
from .string import StringSetting, StringSettingSchema


class FileSettingSchema(StringSettingSchema):
    """
    Marshmallow schema for the FileSetting class.

    """
    must_exist: fields.Field = fields.Boolean()

    @post_load
    def make_instance(self, data: dict) -> 'FileSetting':
        return FileSetting(**data)


class FileSetting(StringSetting):
    """
    A resource adapter setting that represents a path to a file.

    """
    type: str = 'file'
    schema: BaseSettingSchema = FileSettingSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #
        # Whether or not the file must exist
        #
        self.must_exist = kwargs.get('must_exist', True)

    def validate(self, value: str):
        super().validate(value)
        if self.must_exist and not os.path.exists(value):
            raise SettingValidationError('File does not exist')


