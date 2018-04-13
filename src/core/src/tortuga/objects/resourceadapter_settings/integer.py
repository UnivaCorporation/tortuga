from marshmallow import fields, post_load

from .base import BaseSetting, BaseSettingSchema
from .exceptions import SettingValidationError


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
    """
    An integer resource adapter setting.

    """
    type: str = 'integer'
    schema: BaseSettingSchema = IntegerSettingSchema

    def validate(self, value: str):
        if not isinstance(value, int):
            raise SettingValidationError('Value must be a integer')
        super().validate(value)


