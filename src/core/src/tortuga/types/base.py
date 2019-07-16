import json
from typing import Optional, Type

from marshmallow import fields, Schema


class BaseTypeSchema(Schema):
    type: fields.Field = fields.String(dump_only=True)
    id: fields.Field = fields.String()


class BaseType:
    """
    The base object type for Tortuga objects.

    """
    schema_class: Type[Schema] = BaseTypeSchema
    type: str = 'base'

    def __init__(self, **kwargs):
        """
        Initialization.

        :param kwargs: any arguments provided will be assigned as attributes
                       directly on the instance.

        """
        self.id: Optional[str] = kwargs.get('id', None)

    def __str__(self):
        schema_class = self.get_schema_class()
        marshalled = schema_class().dump(self)
        return json.dumps(marshalled.data)

    @classmethod
    def get_schema_class(cls) -> Type[Schema]:
        return cls.schema_class

