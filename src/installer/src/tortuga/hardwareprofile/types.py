from typing import Dict, Optional

from marshmallow import fields

from tortuga.types.base import BaseType, BaseTypeSchema


class HardwareProfileSchema(BaseTypeSchema):
    name = fields.String()
    description = fields.String()
    name_format = fields.String()
    resourceadapter_id = fields.String()
    tags = fields.Dict()


class HardwareProfile(BaseType):
    schema_class = HardwareProfileSchema
    type = 'hardwareprofile'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: Optional[str] = kwargs.get('name', None)
        self.description: Optional[str] = kwargs.get('description', None)
        self.name_format: Optional[str] = kwargs.get('name_format', None)
        self.resourceadapter_id: Optional[str] = kwargs.get('resourceadapter_id', None)
        self.tags: Dict[str, str] = kwargs.get('tags', {})
