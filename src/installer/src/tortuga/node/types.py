from typing import Dict, Optional

from marshmallow import fields, validate

from tortuga.node.state import ALLOWED_NODE_STATES
from tortuga.types.base import BaseType, BaseTypeSchema


NodeStateValidator = validate.OneOf(
    choices=ALLOWED_NODE_STATES,
    error="Invalid node state '{input}'; must be one of {choices}"
)

class NodeSchema(BaseTypeSchema):
    name = fields.String()
    public_hostname = fields.String()
    state = fields.String(validate=NodeStateValidator)
    hardwareprofile_id = fields.String()
    softwareprofile_id = fields.String()
    locked = fields.String()
    tags = fields.Dict()
    last_update = fields.String(dump_only=True)


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
        self.last_update: Optional[str] = kwargs.get('last_update', None)


class NodeStatusSchema(BaseTypeSchema):
    state = fields.String(validate=NodeStateValidator)
    last_update = fields.String(dump_only=True)


class NodeStatus(BaseType):
    schema_class = NodeStatusSchema
    type = 'node'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state: Optional[str] = kwargs.get('state', None)
        self.last_update: Optional[str] = kwargs.get('last_update', None)
