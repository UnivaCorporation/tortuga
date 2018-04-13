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


