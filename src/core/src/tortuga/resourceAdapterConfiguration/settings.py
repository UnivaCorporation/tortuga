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
import re
from typing import Any, List, Union

from marshmallow import fields, Schema


SETTING_TYPES = {}


class SettingNotFoundError(Exception):
    pass


def get_setting_class(type_):
    """
    Gets the setting class for a specified type name.

    :param str type_:             the type name of the setting
    :return:                      the class for the requested type
    :raises SettingNotFoundError: if the setting class is not found

    """
    try:
        return SETTING_TYPES[type_]
    except KeyError:
        raise SettingNotFoundError()


class SettingValidationError(Exception):
    pass


class SettingMeta(type):
    """
    Metaclass for resource adapter settings.

    The purpose of this metaclass is to register settings in a so that they
    can easily be looked-up by type.

    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'BaseSetting':
            return

        SETTING_TYPES[cls.type] = cls


class BaseSettingSchema(Schema):
    """
    Marshmallow schema for resource adapter settings.

    """
    type: fields.Field = fields.String(dump_only=True)
    description: fields.String()
    required: fields.Field = fields.Boolean()
    secret: fields.Field = fields.Boolean()
    mutually_exclusive: fields.Field = fields.List(fields.String())
    requires: fields.Field = fields.List(fields.String())
    overrides: fields.Field = fields.List(fields.String())
    default: fields.Field = fields.String()
    values: fields.Field = fields.List(fields.String())
    list: fields.Field = fields.Boolean()
    list_separator: fields.Field = fields.String()
    advanced: fields.Boolean = fields.Boolean()
    validation_regex: fields.String()


class BaseSetting(metaclass=SettingMeta):
    """
    A resource adapter configuration variable.

    """
    type = None
    schema = None
    validation_regex = None

    def __init__(self, **kwargs):
        self.description = kwargs.get('description', '')
        self.required = kwargs.get('required', False)
        self.secret = kwargs.get('secret', False)
        self.mutually_exclusive = kwargs.get('mutually_exclusive', [])
        self.requires = kwargs.get('requires', [])
        self.overrides = kwargs.get('overrides', [])
        self.default = kwargs.get('default')
        self.values = kwargs.get('values', [])
        self.list = kwargs.get('list', False)
        self.list_separator = kwargs.get('list_separator', ',')
        self.advanced = kwargs.get('advanced', False)
        self.validation_regex = kwargs.get('validation_regex',
                                           self.validation_regex)

    def validate(self, value: str):
        """
        Validates the value against the validation rules for this
        variable.

        :raises SettingValidationError: if the value is not valid, the
                                        exception message will indicate the
                                        problem.

        """
        if not self.type:
            raise Exception('Setting type not set')

        if not isinstance(value, str):
            raise SettingValidationError('Value must be a string')

        #
        # Split as a list prior to validating each value in the list
        #
        if self.list:
            value_list = self._to_list(value)
        else:
            value_list = [value.strip()]

        #
        # Validate each value
        #
        for v in value_list:
            self.validate_regex(v)
            self.validate_values(v)

    def _to_list(self, value: str) -> List[str]:
        return [v.strip() for v in value.split(self.list_separator)]

    def validate_regex(self, value: str):
        if self.validation_regex:
            regex = re.compile(self.validation_regex)
            if regex.fullmatch(value) is None:
                raise SettingValidationError(
                    'Value must match pattern: {}'.format(
                        self.validation_regex)
                )

    def validate_values(self, value: str):
        """
        Validates whether or not the value is one of the required values.
        If values is an empty list, then any value is valid.

        :raises SettingValidationError: if the value is not one of the
                                        required values.

        """
        if self.values and value not in self.values:
            raise SettingValidationError(
                'Value must be one of: {}'.format(self.values))

    def dump(self, value: str) -> Union[str, List[str]]:
        """
        Dumps the string value as a concrete/transformed value.

        :param str value: the value to transform/dump

        :return Union[str, List[str]]: the transformed value

        """
        if self.list:
            return self._to_list(value)
        return value


class BooleanSetting(BaseSetting):
    type = 'boolean'
    schema = BaseSettingSchema
    validation_regex = 'True|False|true|false'

    def dump(self, value: str) -> Union[bool, List[bool]]:
        dumped = super().dump(value)

        if isinstance(dumped, list):
            return [self._to_bool(v) for v in dumped]

        return self._to_bool(dumped)

    def _to_bool(self, v: str):
        return v in ['True', 'true']


class FileSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the FileSetting class.

    """
    must_exist: fields.Field = fields.Boolean()
    base_path: fields.Field = fields.String()


class FileSetting(BaseSetting):
    type = 'file'
    schema = FileSettingSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.must_exist = kwargs.get('must_exist', True)
        self.base_path = kwargs.get('base_path', None)

    def validate(self, value):
        super().validate(value)

        path = self._get_full_path(value)

        if self.must_exist and not os.path.exists(path):
            raise SettingValidationError(
                'File does not exist: {}'.format(path))

    def dump(self, value: str) -> Union[str, List[str]]:
        dumped = super().dump(value)

        if isinstance(dumped, list):
            return [self._get_full_path(v) for v in dumped]

        return self._get_full_path(value)

    def _get_full_path(self, path: str) -> str:
        if not path.startswith('/') and self.base_path:
            path = os.path.join(self.base_path, path)

        return path


class IntegerSetting(BaseSetting):
    type = 'integer'
    schema = BaseSettingSchema
    validation_regex = '[0-9]+'

    def dump(self, value: str) -> Union[int, List[int]]:
        dumped = super().dump(value)

        if isinstance(dumped, list):
            return [int(v) for v in dumped]

        return int(value)


class StringSetting(BaseSetting):
    type = 'string'
    schema = BaseSettingSchema
