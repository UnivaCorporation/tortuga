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

from marshmallow import fields, Schema, post_load


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
    required: fields.Field = fields.Boolean()
    secret: fields.Field = fields.Boolean()
    mutually_exclusive: fields.Field = fields.List(fields.String())
    requires: fields.Field = fields.List(fields.String())


class BaseSetting(metaclass=SettingMeta):
    """
    A resoruce adapter configuration variable.

    """
    type = None
    schema = None

    def __init__(self, **kwargs):
        self.description = kwargs.get('description', '')
        self.required = kwargs.get('required', False)
        self.secret = kwargs.get('secret', False)
        self.values = kwargs.get('values', [])
        self.mutually_exclusive = kwargs.get('mutually_exclusive', [])
        self.default = kwargs.get('default')

    def validate(self, value):
        """
        Validates the value against the validation rules for this
        variable.

        :raises SettingValidationError: if the value is not valid, the
                                        exception message will indicate the
                                        problem.

        """
        if not self.type:
            raise Exception('Setting type not set')
        self.validate_values(value)

    def validate_values(self, value):
        """
        Validates whether or not the value is one of the required values.
        If values is an empty list, then any value is valid.

        :raises SettingValidationError: if the value is not one of the
                                        required values.

        """
        if self.values and value not in self.values:
            raise SettingValidationError(
                'Value must be one of: {}'.format(self.values))


class BooleanSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the BooleanSetting class.
    """
    default: fields.Field = fields.Boolean()

    @post_load
    def make_instance(self, data: dict) -> 'BooleanSetting':
        return BooleanSetting(**data)


class BooleanSetting(BaseSetting):
    type = 'boolean'
    schema = BooleanSettingSchema

    def validate(self, value):
        if not isinstance(value, bool):
            raise SettingValidationError('Value must be an boolean')
        super().validate(value)


class StringSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the StringSetting class.
    """
    default: fields.Field = fields.String()
    values: fields.Field = fields.List(fields.String())

    @post_load
    def make_instance(self, data: dict) -> 'StringSetting':
        return StringSetting(**data)


class FileSettingSchema(StringSettingSchema):
    """
    Marshmallow schema for the FileSetting class.
    """
    must_exist: fields.Field = fields.Boolean()

    @post_load
    def make_instance(self, data: dict) -> 'FileSetting':
        return FileSetting(**data)


class FileSetting(BaseSetting):
    type = 'file'
    schema = FileSettingSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.must_exist = kwargs.get('must_exist', True)

    def validate(self, value):
        if not isinstance(value, str):
            raise SettingValidationError('File name must be a string')
        super().validate(value)
        if self.must_exist and not os.path.exists(value):
            raise SettingValidationError('File does not exist')


class IntegerSettingSchema(BaseSettingSchema):
    """
    Marshmallow schema for the IntegerSetting class.
    """
    default: fields.Field = fields.Integer()
    values: fields.Field = fields.List(fields.Integer())

    @post_load
    def make_instance(self, data: dict) -> 'IntegerSetting':
        return IntegerSetting(**data)


class IntegerSetting(BaseSetting):
    type = 'integer'
    schema = IntegerSettingSchema

    def validate(self, value):
        if not isinstance(value, int):
            raise SettingValidationError('Value must be a integer')
        super().validate(value)


class StringSetting(BaseSetting):
    type = 'string'
    schema = StringSettingSchema

    def validate(self, value):
        if not isinstance(value, str):
            raise SettingValidationError('Value must be a string')
        super().validate(value)
