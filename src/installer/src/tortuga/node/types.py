from typing import Dict, Optional

from marshmallow import fields

from tortuga.types.base import BaseType, BaseTypeSchema


class NodeSchema(BaseTypeSchema):
    name = fields.String()
    public_hostname = fields.String()
    state = fields.String()
    hardwareprofile_id = fields.String()
    softwareprofile_id = fields.String()
    locked = fields.String()
    tags = fields.Dict()


class Node(BaseType):
    schema_class = NodeSchema
    type = 'node'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: Optional[str] = kwargs.get('name', None)
        self.public_hostname: Optional[str] = kwargs.get('public_hostname', None)
        self.state: Optional[str] = kwargs.get('state', None)
        self.hardwareprofile_id: Optional[str] = kwargs.get('hardwareprofile_id', None)
        self.softwareprofile_id: Optional[str] = kwargs.get('softwareprofile_id', None)
        self.locked: Optional[str] = kwargs.get('locked', None)
        self.tags: Dict[str, str] = kwargs.get('tags', {})
