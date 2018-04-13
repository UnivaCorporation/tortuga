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


