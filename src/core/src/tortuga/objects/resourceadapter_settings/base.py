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

from typing import Any, Dict, List, Type

from marshmallow import Schema, fields

from .exceptions import SettingNotFoundError, SettingValidationError


#
# Dictionary, storing registered settings classes
#
SETTING_TYPES: Dict[str, Type['BaseSetting']] = {}


def get_setting_class(type_: str) -> Type['BaseSetting']:
    """
    Gets the setting class for a specified type name.

    :param str type_:             the type name of the setting
    :return BaseSetting:          the class for the requested type
    :raises SettingNotFoundError: if the setting class is not found

    """
    try:
        return SETTING_TYPES[type_]
    except KeyError:
        raise SettingNotFoundError()


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
    A resource adapter configuration setting. This class is designed to be
    extended in order to define specific setting types.

    """
    #
    # The short type name for this setting
    #
    type: str = None
    #
    # The marshmallow schema for this class
    #
    schema: BaseSettingSchema = None

    def __init__(self, **kwargs):
        #
        # The default value for this setting
        #
        self.default: Any = kwargs.get('default', None)
        #
        # A description of this setting
        #
        self.description: str = kwargs.get('description', '')
        #
        # Whether or not this setting is required
        #
        self.required: bool = kwargs.get('required', False)
        #
        # Whether or not this value contains sensitive/secret information
        #
        self.secret: bool = kwargs.get('secret', False)
        #
        # Possible values that can be used for this setting
        #
        self.values: List[Any] = kwargs.get('values', [])
        #
        # If this setting is used, the settings in this list must also
        # be present
        #
        self.requires: List[str] = kwargs.get('requires', [])
        #
        # If this settings is used, the settings in this list must not
        # be present
        #
        self.mutually_exclusive: List[str] = \
            kwargs.get('mutually_exclusive', [])

    def validate(self, value: Any):
        """
        Validates the value against the validation rules for this
        variable.

        :raises SettingValidationError: if the value is not valid, the
                                        exception message will indicate the
                                        problem.

        """
        if not self.type:
            raise Exception('Setting type not set')
        self.validate_values()

    def validate_values(self, value: Any):
        """
        Validates whether or not the value is one of the required values.
        If values is an empty list, then any value is valid.

        :raises SettingValidationError: if the value is not one of the
                                        required values.

        """
        if self.values and value not in self.values:
            raise SettingValidationError(
                'Value must be one of: {}'.format(self.values))


