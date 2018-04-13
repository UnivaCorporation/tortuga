from marshmallow.schema import Schema
from marshmallow import fields, post_load


class BaseSettingSchema(Schema):
    type = fields.String(dump_only=True)
    required = fields.Boolean()
    secret = fields.Boolean()
    mutually_exclusive = fields.List(fields.String())


class BooleanSettingSchema(BaseSettingSchema):
    @post_load
    def make_instance(self, data):
        from ..resourceadapter_settings import BooleanSetting
        return BooleanSetting(**data)


class FileSettingSchema(BaseSettingSchema):
    must_exist = fields.Boolean()
    values = fields.List(fields.String())

    @post_load
    def make_instance(self, data):
        from ..resourceadapter_settings import FileSetting
        return FileSetting(**data)


class IntegerSettingSchema(BaseSettingSchema):
    values = fields.List(fields.Integer())

    @post_load
    def make_instance(self, data):
        from ..resourceadapter_settings import IntegerSetting
        return IntegerSetting(**data)


class StringSettingSchema(BaseSettingSchema):
    values = fields.List(fields.String())

    @post_load
    def make_instance(self, data):
        from ..resourceadapter_settings import StringSetting
        return StringSetting(**data)
