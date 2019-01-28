# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
