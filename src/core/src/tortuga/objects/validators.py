import re
from typing import Any, Dict, Optional


class FieldValidationError(Exception):
    pass


class BaseValidator:
    def __init__(self, **kwargs):
        self.required = kwargs.get('required', False)
        
    def validate(self, value: Any):
        if self.required and value is None:
            raise FieldValidationError('Value is required')


class StringValidator(BaseValidator):
    def validate(self, value: str):
        super().validate(value)

        if not isinstance(value, str):
            raise FieldValidationError(
                'Value must be a string: {}'.format(value))


class RegexValidator(StringValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pattern = kwargs['pattern']

    def validate(self, value: str):
        super().validate(value)
        
        regex = re.compile(self.pattern)
        if regex.fullmatch(value) is None:
            raise FieldValidationError(
                'Value must match pattern: {}'.format(self.pattern))


class ValidationError(Exception):
    def __init__(self,
                 errors: Optional[Dict[str, FieldValidationError]] = None,
                 *args, **kwargs):
        self.errors = {}
        if errors:
            self.errors = errors

        super().__init__(*args, **kwargs)

    def __str__(self):
        return str({k: str(v) for k, v in self.errors.items()})


class ValidatorMixin:
    validators: Dict[str, BaseValidator] = {}

    def validate(self) -> None:
        errors = {}

        for k, validator in self.validators.items():
            try:
                validator.validate(self.get(k, None))

            except FieldValidationError as err:
                errors[k] = err

        if errors:
            raise ValidationError(errors)
