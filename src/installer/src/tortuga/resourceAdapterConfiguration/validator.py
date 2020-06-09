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

from collections.abc import MutableMapping
from typing import Any, Dict, Optional, Iterator

from .settings import BaseSetting, SettingValidationError


class ValidationError(Exception):
    """
    This class represents a resource adapter configuration validation
    error. It contains a dict of errors, one for each setting that raised
    an error during the validation process.

    """
    def __init__(self,
                 errors: Optional[Dict[str, SettingValidationError]] = None,
                 *args, **kwargs):
        self.errors = {}
        if errors:
            self.errors = errors
        super().__init__(*args, **kwargs)

    def __str__(self):
        return str({k: str(v) for k, v in self.errors.items()})


class ConfigurationValidator(MutableMapping):
    """
    This class represents a validator for a resource adapter configuration.

    """
    def __init__(self, settings: Optional[Dict[str, BaseSetting]] = None):
        """
        Initialization.

        :param Optional[Dict[str, BaseSetting]] settings: the settings
                                                          definition for the
                                                          resource adapter

        """
        self._settings: Dict[str, BaseSetting] = {}
        if settings:
            self._settings = settings

        self._storage: Dict[str, str] = {}

        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """
        Initialize all settings that have default values set.

        """
        for k, v in self._settings.items():
            if v.default:
                self[k] = v.default

    def __setitem__(self, k: str, v: Optional[str]):
        #
        # Setting a key to None should delete it if it exists, and
        # do nothing if it does not exist
        #
        if v is None:
            self._storage.pop(k, None)
            return
        #
        # Validate the key type
        #
        if not isinstance(k, str):
            raise ValueError(
                'Only strings can be used for keys: {}'.format(k))
        #
        # validate the value type
        #
        if not isinstance(v, str):
            raise ValueError(
                'Only strings can be used for values: {}'.format(v)
            )
        return self._storage.__setitem__(k, v)

    def __delitem__(self, v: str):
        return self._storage.__delitem__(v)

    def __getitem__(self, k: str) -> Optional[str]:
        return self._storage.__getitem__(k)

    def __len__(self) -> int:
        return self._storage.__len__()

    def __iter__(self) -> Iterator[str]:
        return self._storage.__iter__()

    def __str__(self) -> str:
        return self._storage.__str__()

    def validate(self, full: bool = True) -> None:
        """
        Validate the resource adapter settings profile.

        :param bool full: perform a full validation. A full validation
                          validates required fields, mutually exclusive,
                          and requires. A partial validation makes sure
                          that non-valid field names are not permitted,
                          and validates the content of any existing
                          fields.

        :raises: SettingValidationError

        """
        errors = {}

        #
        # Make sure all of the settings are known
        #
        for k in self._storage.keys():
            if k not in self._settings.keys():
                errors[k] = SettingValidationError('Invalid setting name')

        #
        # Validate each setting
        #
        for k, v in self._settings.items():
            try:
                if k in self._storage.keys():
                    v.validate(self._storage[k])
                if full:
                    self._validate_required(k, v)
                    #
                    # Don't bother validating if the key isn't set
                    #
                    if self._storage.get(k, "") != "":
                        #
                        # Dump as transformed/realized value
                        #
                        val = v.dump(self._storage[k])
                        #
                        # By default everything should validate dependencies
                        #
                        should_validate = True
                        #
                        # Booleans should only validate dependencies if their
                        # value is true
                        #
                        if isinstance(val, bool):
                            should_validate = val
                        #
                        # Strings, lists, and dicts should only validate
                        # dependencies if they are truthy
                        #
                        if isinstance(val, (str, dict, list)):
                            should_validate = bool(val)
                        #
                        # Validate dependencies
                        #
                        if should_validate:
                            self._validate_requires(v)
                            self._validate_mutually_exclusive(v)
            except SettingValidationError as err:
                errors[k] = err

        if errors:
            raise ValidationError(errors)

    def _validate_required(self, k: str, v: BaseSetting):
        """
        Validates the required flag on a setting.

        :param str k: the key to validate
        :param BaseSetting v: the setting to validate

        :raises: SettingValidationError

        """
        if not v.required:
            return

        if k in self._storage.keys():
            return

        if v.mutually_exclusive:
            for alternate_key in v.mutually_exclusive:
                if alternate_key in self._storage.keys():
                    return
            valid_values = ', '.join(v.mutually_exclusive)

            raise SettingValidationError(
                'This or {} is required'.format(valid_values))

        else:
            raise SettingValidationError('Setting is required')

    def _validate_requires(self, v: BaseSetting):
        """
        Validates the requires flag on a setting.

        :param BaseSetting v: the setting to validate

        raises: SettingValidationError

        """
        if not v.requires:
            return

        for rk in v.requires:
            if rk not in self._storage.keys():
                raise SettingValidationError(
                    'Requires {}'.format(rk))

    def _validate_mutually_exclusive(self, v: BaseSetting) -> None:
        """
        Validates the mutually exclusive flag on a setting.

        :param BaseSetting v: the setting to validate

        :raises: SettingValidationError

        """
        if not v.mutually_exclusive:
            return

        for mk in v.mutually_exclusive:
            if mk in self._storage.keys():
                raise SettingValidationError(
                    'Mutually exclusive with {}'.format(mk))

    def dump(self) -> Dict[str, Any]:
        """
        Dumps as a plain dict, with values transformed into their concrete
        data types. A partial validation is performed prior to dumping to
        ensure that any transformations will succeed.

        :return Dict[str, Any]: a dict of the transformed data

        """
        self.validate(full=False)

        result = {}

        for k, v in self._storage.items():
            setting: BaseSetting = self._settings[k]
            result[k] = setting.dump(v)

        return result

    def load(self, data: Dict[str, str]):
        """
        Loads a plain dict, expecting string values only for both keys
        and values. If one of the values of the dict is not a string,
        it will be converted to one prior to storing.

        :param dict data: the data dict to load for validation

        """
        for k, v in data.items():
            #
            # Fail silently if the setting isn't found, we will
            # let validation take care of that instead
            #
            setting: BaseSetting = self._settings.get(k)
            if setting:
                #
                # Override settings, if required
                #
                for override in setting.overrides:
                    if override in self._storage.keys():
                        self._storage.pop(override)
            self[k] = v
