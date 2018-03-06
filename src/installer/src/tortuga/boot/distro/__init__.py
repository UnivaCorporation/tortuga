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
import os
import pkgutil
from typing import Generator, Any
from .base import DistributionBase
from tortuga.exceptions.osNotSupported import OsNotSupported


class DistributionFactory(object):
    """
    Return matching OS class to URI.
    """
    def __init__(self, uri: str) -> None:
        """
        :return: None
        """
        self._uri: str = uri
        self._lookup_class: Any = DistributionBase

    def __call__(self) -> DistributionBase:
        """
        :return: DistributionBase
        """
        for module in self._discover_distributions():
            for distribution in module:
                if not distribution.__abstract__:
                    try:
                        instantiated: Any = distribution(self._uri)
                        if instantiated.matches_path():
                            return instantiated
                    except OsNotSupported:
                        continue

    def _discover_distributions(self) -> Any:
        """
        Find all subclass of cls in py files located in subdirectory 'path'.

        :returns:
        """
        base_path: str = os.path.dirname(__file__)
        for _, base_distro, _ in pkgutil.walk_packages([base_path]):
            if not base_distro == 'base':
                for file_name in os.listdir(os.path.join(base_path, base_distro)):
                    module_name: str = file_name.split('.')[0]
                    yield self._look_for_classes(__name__ + '.' + base_distro + '.' + module_name)

    def _look_for_classes(self, module_name: str) -> Generator[DistributionBase, None, None]:
        """
        :param module_name: String
        :return: DistributionBase
        """
        try:
            module: Any = __import__(module_name)
        except OsNotSupported:
            return

        # Walk the dictionaries to get to the last one
        d: dict = module.__dict__
        for m in module_name.split('.')[1:]:
            d: dict = d[m].__dict__

        # Search dictionary for subclasses of 'cls'
        for key, entry in d.items():
            if key == self._lookup_class.__name__:
                continue
            try:
                if issubclass(entry, self._lookup_class):
                    yield entry
            except TypeError:
                # This happens when a non-type is passed to issubclass. We
                # don't care as it can't be a subclass of cls if it isn't
                # a type
                continue
