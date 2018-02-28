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
import urllib.error
import urllib.parse
import urllib.request
import logging
from typing import Optional, Dict
from tortuga.objects import osInfo
from tortuga.helper import osHelper


class DistributionPrimitivesBase(dict):
    """
    Represent locations of needed primitives
    from the distribution.

    TODO: This needs to be implemented better
    """
    def __new__(cls, isolinux_dir: str, isolinux_bin: str, kernel: str, initrd: str,
                 images_dir: str, base_os_dir: str, packages_dir: str, repo_data_dir: str,
                 **kwargs : str) -> Dict[str, str]:
        """
        :param isolinux_dir: String
        :param isolinux_bin: String
        :param kernel: String
        :param initrd: String
        :param images_dir: String
        :param base_os_dir: String
        :param packages_dir: String
        :param repo_data_dir: String
        :param kwargs: String, String set the name of the primitive and its path
        :return: None
        """
        primitives: Dict[str, str] = {
            'isolinux_dir': isolinux_dir,
            'isolinux_bin': isolinux_bin,
            'kernel': kernel,
            'initrd': initrd,
            'images_dir': images_dir,
            'base_os_dir': base_os_dir,
            'packages_dir': packages_dir,
            'repo_data_dir': repo_data_dir
        }

        for primitive, path in kwargs.items():
            primitives[primitive] = path

        return primitives


class DistributionBase(object):
    """
    Represents an install source of a distribution.
    """
    __abstract__ = True

    def __init__(self, source_path: str, name: str, major: int, minor: int, architecture: str = 'x84_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param name: String name of distribution
        :param major: Integer major minor version of distribution
        :param minor: Integer minor minor version of distribution
        :param architecture: String targeted architecture
        :return: None
        """
        self._source_path = str(source_path)
        self._name = str(name.lower())
        self._major = int(major)
        self._minor = int(minor)
        self._architecture = str(architecture)

        self._source_uri = urllib.parse.urlparse(self._source_path)

        self._logger = logging.getLogger(
            'tortuga.boot.distro.{}'.format(self.__class__.__name__)
        )
        self._logger.addHandler(logging.NullHandler())

        self._primitives: Optional[DistributionPrimitivesBase] = None

    @property
    def source_path(self) -> str:
        """
        :return: String
        """
        return self._source_path

    @source_path.setter
    def source_path(self, value: str) -> None:
        """
        :param value: String
        :return: None
        """
        self._source_path = str(value)
        self._source_uri = urllib.parse.urlparse(value)

    @property
    def name(self) -> str:
        """
        :return: String
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        :param value: String
        :return: None
        """
        self._name = str(value.lower())

    @property
    def version(self) -> str:
        """
        :return: Integer
        """
        return '{}.{}'.format(self.major, self.minor)

    @property
    def major(self) -> int:
        """
        :return: Integer
        """
        return self._major

    @major.setter
    def major(self, value: int) -> None:
        """
        :param value: Integer
        :return: None
        """
        self._major = int(value)

    @property
    def minor(self) -> int:
        """
        :return: Integer
        """
        return self._minor

    @minor.setter
    def minor(self, value: int) -> None:
        """
        :param value: Integer
        :return: None
        """
        self._minor = int(value)

    @property
    def architecture(self) -> str:
        """
        :return: String
        """
        return self._architecture

    @architecture.setter
    def architecture(self, value: str) -> None:
        """
        :param value: String
        :return: None
        """
        self._architecture = str(value)

    @property
    def is_remote(self) -> bool:
        """
        :return: Boolean
        """
        return self._source_uri.scheme in ('http', 'https')

    @property
    def is_source_valid(self) -> bool:
        """
        :return: Boolean
        """
        if self.is_remote:
            req = urllib.request.Request(self.source_path, method='HEAD')
            try:
                urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return False
                else:
                    raise  # Don't swallow other network errors
            return True
        else:
            return os.path.isfile(self.source_path)

    def _update_version(self) -> None:
        """
        Once matched, update version
        numbers.

        :return: None
        """
        # Implement in child class.
        raise NotImplementedError

    def _matches_remote(self) -> bool:
        """
        :return: Boolean
        """
        count: int = 0
        target: int = len(self._primitives.keys())

        for primitive, path in self._primitives.items():
            url = os.path.join(self._source_path, path)
            request = urllib.request.Request(
                url=url,
                method='HEAD'
            )
            try:
                response = urllib.request.urlopen(request)
                if response.code == 200:
                    count += 1
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                else:
                    raise  # Could be a connection issue

        if count == target:
            return True

        return False

    def _matches_local(self) -> bool:
        """
        :return: Boolean
        """
        count: int = 0
        target: int = len(self._primitives.keys())

        for primitive, path in self._primitives.items():
            if os.path.exists(path):
                count += 1

        if count == target:
            return True

        return False

    def matches_path(self) -> bool:
        """
        Evaluate whether primitives match source media,

        :return: Boolean
        """
        if not self._primitives:
            raise NotImplementedError

        if self.is_remote:
            matches = self._matches_remote()
        else:
            matches = self._matches_local()

        if matches:
            self._update_version()
            return matches

        return matches

    def get_logger(self) -> logging.Logger:
        """
        :return: Logger
        """
        return self._logger

    def get_os_info(self) -> osInfo:
        """
        :return: OsInfo
        """
        return osHelper.getOsInfo(
            self.name,
            self.version,
            self.architecture
        )
