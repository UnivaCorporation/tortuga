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
from ..base import DistributionBase, DistributionPrimitivesBase

class RedHat6Primitives(DistributionPrimitivesBase):
    """
    Represent locations of needed primitives
    from the Red Hat 6 like distributions.
    """
    def __new__(cls) -> Dict[str, str]:
        """
        :return: None
        """
        return super(RedHat6Primitives, cls).__new__(
            cls,
            isolinux_dir='isolinux',
            isolinux_bin='isolinux/isolinux.bin',
            kernel='isolinux/isolinux.bin',
            initrd='isolinux/initrd.img',
            images_dir='images',
            base_os_dir='Packages',
            packages_dir='Packages',
            repo_data_dir='repodata',
            rpm_gpg_key='RPM-GPG-KEY-redhat-release'
        )


class RedHat6(DistributionBase):
    """
    Represents a Red Hat 6 distribution.
    """
    __abstract__ = False

    def __init__(self, source_path: str, architecture: str = 'x84_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param architecture: String targeted architecture
        :returns: None
        """
        super(RedHat6, self).__init__(
            source_path,
            'redhat',
            6,
            0,
            architecture
        )

        self._primitives: DistributionPrimitivesBase = RedHat6Primitives()

    def _update_version(self):
        """
        :return: None
        """
        pass  # TODO
