import os.path

from . import schemas


class ValidationError(Exception):
    pass


class ConfigVariable:
    """
    A resoruce adapter configuration variable.

    """
    type = None
    schema = None

    def __init__(self, **kwargs):
        self.description = kwargs.get('description', '')
        self.required = kwargs.get('required', False)
        self.secret = kwargs.get('secret', False)
        self.values = kwargs.get('values', [])
        self.mutually_exclusive = kwargs.get('mutually_exclusive', [])

    def validate(self, value):
        """
        Validates the value against the validation rules for this
        variable.

        :raises ValidationError: if the value is not valid, the exception
                                 message will indicate the problem.

        """
        if not self.type:
            raise Exception('Variable type not set')
        self.validate_values()

    def validate_values(self, value):
        """
        Validates whether or not the value is one of the required values.
        If values is an empty list, then any value is valid.

        :raises ValidationError: if the value is not one of the required
                                 values.

        """
        if self.values and value not in self.values:
            raise ValidationError(
                'Value must be one of: {}'.format(self.values))


class BooleanVariable(ConfigVariable):
    type = 'boolean'
    schema = schemas.BooleanVariableSchema

    def validate(self, value):
        if not isinstance(value, bool):
            raise ValidationError('Value must be an boolean')
        super().validate(value)


class FileVariable(ConfigVariable):
    type = 'file'
    schema = schemas.FileVariableSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.must_exist = kwargs.get('must_exist', True)

    def validate(self, value):
        if not isinstance(value, str):
            raise ValidationError('File name must be a string')
        super().validate(value)
        if self.must_exist and not os.path.exists(value):
            raise ValidationError('File does not exist')


class IntegerVariable(ConfigVariable):
    type = 'integer'
    schema = schemas.IntegerVariableSchema

    def validate(self, value):
        if not isinstance(value, int):
            raise ValidationError('Value must be a integer')
        super().validate(value)


class StringVariable(ConfigVariable):
    type = 'string'
    schema = schemas.StringVariableSchema

    def validate(self, value):
        if not isinstance(value, str):
            raise ValidationError('Value must be a string')
        super().validate(value)
