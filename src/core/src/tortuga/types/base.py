from typing import Optional, Type

from marshmallow import fields, Schema


class BaseTypeSchema:
    type: fields.Field = fields.String(dump_only=True)
    id: fields.Field = fields.String()


class BaseType:
    """
    The base object type for Tortuga objects.

    """
    schema: Type[Schema] = BaseTypeSchema
    type: str = None

    def __init__(self, **kwargs):
        """
        Initialization.

        :param kwargs: any arguments provided will be assigned as attributes
                       directly on the instance.

        """
        self.id: Optional[str] = None

        for k, v in kwargs.items():
            setattr(self, k, v)
