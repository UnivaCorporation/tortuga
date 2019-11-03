from typing import Optional

from marshmallow import fields

from tortuga.types.base import BaseType, BaseTypeSchema


class TagSchema(BaseTypeSchema):
    value = fields.String()


class Tag(BaseType):
    schema_class = TagSchema
    type = 'tag'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value: Optional[str] = kwargs.get('value', None)
