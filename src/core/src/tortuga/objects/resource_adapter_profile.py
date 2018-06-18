from collections.abc import MutableMapping
from typing import Dict, Optional, _KT, _VT_co, Iterator, _T_co, _VT

from .resource_adapter_settings import BaseSetting, SettingValidationError


class ResourceAdapterProfile(MutableMapping):
    """
    This class represents a group of settings for a resource adapter profile.

    """
    def __init__(self, settings: Optional[Dict[str, BaseSetting]] = None):
        """
        Initialization.

        :param Optional[Dict[str, BaseSetting]] settings: the settings
                                                          definition for the
                                                          resource adapter

        """
        if settings:
            self._settings = settings
        else:
            self._settings = {}

        self._storage = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """
        Initialize all settings that have default values set.

        """
        for k, v in self._settings.items():
            if v.default:
                self[k] = v.default

    def __setitem__(self, k: _KT, v: _VT) -> None:
        return self.__setitem__(k, v)

    def __delitem__(self, v: _KT) -> None:
        return self._storage.__delitem__(v)

    def __getitem__(self, k: _KT) -> _VT_co:
        return self.__getitem__(k)

    def __len__(self) -> int:
        return self._storage.__len__()

    def __iter__(self) -> Iterator[_T_co]:
        return self._storage.__iter__()

    def validate(self) -> None:
        """
        Validate the resource adapter settings profile.

        :raises: SettingValidationError

        """
        #
        # Make sure all of the settings are known
        #
        for k in self._storage.keys():
            if k not in self._settings.keys():
                raise SettingValidationError('Unknown setting: {}'.format(k))

        #
        # Validate each setting
        #
        for k, v in self._settings.items():
            self._validate_required(k, v)
            self._validate_mutually_exclusive(k, v)
            if k in self._storage.keys():
                v.validate(self._storage[k])

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
            raise SettingValidationError('Setting is required: {}'.format(k))

    def _validate_mutually_exclusive(self, k: str, v: BaseSetting) -> None:
        """
        Validates the mutually exclusive flag on a setting.

        :param str k: the key to validate
        :param BaseSetting v: the setting to validate

        :raises: SettingValidationError

        """
        if not v.mutually_exclusive:
            return

        for mk in v.mutually_exclusive:
            if mk in self._storage.keys():
                raise SettingValidationError(
                    'Mutually exclusive: {} and {}'.format(k, mk))