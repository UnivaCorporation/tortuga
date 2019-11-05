from typing import Optional, Tuple

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

    @staticmethod
    def parse_id(id_: str) -> Tuple[str, str, str]:
        """
        Parses a tag ID into it's respective parts:

            <object_type>:<object_id>:<tag_name>

        :param id_: the tag ID to parse

        :return Tuple[str, str, str]: a tuple of the parsed parts

        """
        id_parts = id_.split(":")
        if len(id_parts) < 3:
            raise Exception('Invalid tag ID: {}'.format(id_))
        object_type = id_parts.pop(0)
        object_id = id_parts.pop(0)
        tag_name = ":".join(id_parts)

        return object_type, object_id, tag_name
