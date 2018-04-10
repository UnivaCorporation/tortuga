from marshmallow.schema import Schema
from marshmallow import fields as marsmallow_fields


class BaseVariableSchema(Schema):
    type = marsmallow_fields.String(dump_only=True)
    required = marsmallow_fields.Boolean()
    secret = marsmallow_fields.Boolean()
    mutually_exclusive = marsmallow_fields.List(marsmallow_fields.String())


class BooleanVariableSchema(BaseVariableSchema):
    pass


class FileVariableSchema(BaseVariableSchema):
    must_exist = marsmallow_fields.Boolean()
    values = marsmallow_fields.List(marsmallow_fields.String())


class IntegerVariableSchema(BaseVariableSchema):
    values = marsmallow_fields.List(marsmallow_fields.Integer())


class StringVariableSchema(BaseVariableSchema):
    values = marsmallow_fields.List(marsmallow_fields.String())
