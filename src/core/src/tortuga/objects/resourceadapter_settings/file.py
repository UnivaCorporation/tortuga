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


