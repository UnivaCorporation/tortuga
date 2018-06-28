from collections.abc import MutableMapping
from typing import Dict, Optional, Iterator

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
        return str(self.errors)


class ConfigurationValidator(MutableMapping):
    """
    This class represents a validator for a resource adapter configuration.

    """
    REDACTED_STRING = '**********'

    def __init__(self, settings: Optional[Dict[str, BaseSetting]] = None):
        """
        Initialization.

        :param Optional[Dict[str, BaseSetting]] settings: the settings
                                                          definition for the
                                                          resource adapter

        """
        self._settings = {}
        if settings:
            self._settings = settings

        self._storage = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """
        Initialize all settings that have default values set.

        """
        for k, v in self._settings.items():
            if v.default:
                self[k] = v.default

    def __setitem__(self, k: str, v: str) -> None:
        return self._storage.__setitem__(k, v)

    def __delitem__(self, v: str) -> None:
        return self._storage.__delitem__(v)

    def __getitem__(self, k: str):
        return self._storage.__getitem__(k)

    def __len__(self) -> int:
        return self._storage.__len__()

    def __iter__(self) -> Iterator[str]:
        return self._storage.__iter__()

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
                errors[k] = SettingValidationError('Unknown setting')

        #
        # Validate each setting
        #
        for k, v in self._settings.items():
            try:
                if full:
                    self._validate_required(k, v)
                    self._validate_requires(v)
                    self._validate_mutually_exclusive(v)
                if k in self._storage.keys():
                    v.validate(self._storage[k])
            except SettingValidationError as err:
                errors[k] = err

        if errors:
            raise ValidationError(errors)

    def _validate_required(self, k: str, v: BaseSetting) -> None:
        """
        Validates the required flag on a setting.

        :param str k: the key to validate
        :param BaseSetting v: the setting to validate

        :raises: SettingValidationError

        """
        if not v.required:
            return

        if k not in self._storage.keys():
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

    def dump(self, secure: bool = True) -> Dict[str, str]:
        """
        Dumps as a plain dict. A partial validation is performed prior to
        dumping the data.

        :param bool secure: Whether or not to redact secure values from the
                            dumped output.

        :return dict: a dict of the data
        :raises ResourceAdapterProfileValidationError:

        """
        self.validate(full=False)

        result = {}

        for k, v in self._storage.items():
            v_out = v

            if secure and self._settings[k].secret:
                v_out = self.REDACTED_STRING

            result[k] = v_out

        return result

    def load(self, data: Dict[str, str]):
        """
        Loads a plain dict. Performs a partial validation of the data after
        performing the load.

        :param dict data: the data dict to load and validate

        :raises ResourceAdapterProfileValidationError:

        """
        for k, v in data.items():
            self[k] = v
        self.validate(full=False)
