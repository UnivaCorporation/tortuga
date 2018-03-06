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
from typing import Dict
from .base import RedHatFamily, RedHatFamilyPrimitives


class RedHat7Primitives(RedHatFamilyPrimitives):
    """
    Represent locations of needed primitives
    from the Red Hat 7 distributions.
    """
    def __new__(cls) -> Dict[str, str]:
        """
        :return: None
        """
        return super(RedHat7Primitives, cls).__new__(cls, rpm_gpg_key='RPM-GPG-KEY-redhat-release')


class RedHat7(RedHatFamily):
    """
    Represents a Red Hat 7 distribution.
    """
    __abstract__: bool = False

    def __init__(self, source_path: str, architecture: str = 'x84_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param architecture: String targeted architecture
        :returns: None
        """
        super(RedHat7, self).__init__(
            source_path,
            'rhel',
            7,
            0,
            architecture
        )

        self._primitives: RedHat7Primitives = RedHat7Primitives()

    @property
    def release_package(self) -> str:
        """
        :return: String
        """
        return 'redhat-release-server'
