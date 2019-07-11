from typing import Dict, Optional

from marshmallow import fields

from tortuga.types.base import BaseType, BaseTypeSchema


class SoftwareProfileSchema(BaseTypeSchema):
    name = fields.String()
    description = fields.String()
    min_nodes = fields.Integer()
    max_nodes = fields.Integer()
    locked = fields.String()
    data_root = fields.String()
    data_rsync = fields.String()
    tags = fields.Dict()


class SoftwareProfile(BaseType):
    schema_class = SoftwareProfileSchema
    type = 'softwareprofile'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: Optional[str] = kwargs.get('name', None)
        self.description: Optional[str] = kwargs.get('description', None)
        self.min_nodes: int = kwargs.get('min_nodes', -1)
        self.max_nodes: int = kwargs.get('max_nodes', 25)
        self.locked: Optional[str] = kwargs.get('locked', None)
        self.data_root: Optional[str] = kwargs.get('data_root', None)
        self.data_rsync: Optional[str] = kwargs.get('data_rsync', None)
        self.tags: Dict[str, str] = kwargs.get('tags', {})
