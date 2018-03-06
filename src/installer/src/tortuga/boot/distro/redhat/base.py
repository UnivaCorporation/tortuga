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
import subprocess
from typing import Dict
from jinja2 import Template
from tempfile import NamedTemporaryFile, TemporaryDirectory
from ..base import DistributionBase, DistributionPrimitivesBase


REPO_CONFIGURATION_TEMPLATE = """[main]
cachedir=/tmp/cache/yum/$basearch/$releasever
keepcache=0
debuglevel=2
logfile=/var/log/yum.log
exactarch=1
obsoletes=1
gpgcheck=1
plugins=0
installonly_limit=5
[temp]
name=temp
baseurl={{ base_url }}
gpgcheck=1
gpgkey={{ gpg_key }}
enabled = 1
"""


class RedHatFamilyPrimitives(DistributionPrimitivesBase):
    """
    Represent locations of needed primitives
    from any Red Hat like distributions.
    """
    def __new__(cls, rpm_gpg_key: str) -> Dict[str, str]:
        """
        :return: None
        """
        return super(RedHatFamilyPrimitives, cls).__new__(
            cls,
            isolinux_dir='isolinux',
            isolinux_bin='isolinux/isolinux.bin',
            kernel='isolinux/isolinux.bin',
            initrd='isolinux/initrd.img',
            images_dir='images',
            base_os_dir='Packages',
            packages_dir='Packages',
            repo_data_dir='repodata',
            rpm_gpg_key=rpm_gpg_key
        )


class RedHatFamily(DistributionBase):
    """
    Represents any Red Hat like distribution.
    """
    __abstract__: bool = True

    def __init__(self, source_path: str, name: str, major: int, minor: int, architecture: str = 'x84_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param name: String name of distribution
        :param major: Integer major minor version of distribution
        :param minor: Integer minor minor version of distribution
        :param architecture: String targeted architecture
        :return: None
        """

        super(RedHatFamily, self).__init__(
            source_path,
            name,
            major,
            minor,
            architecture
        )

    def _update_version(self) -> None:
        """
        :return: None
        """
        template: Template = Template(REPO_CONFIGURATION_TEMPLATE)

        if self.is_remote:
            context: Dict[str, str] = {
                'base_url': self._source_path,
                'gpg_key': os.path.join(self._source_path, self._primitives['rpm_gpg_key'])
            }
        else:
            context: Dict[str, str] = {
                'base_url': 'file://{}'.format(self._source_path),
                'gpg_key': 'file://{}'.format(os.path.join(self._source_path, self._primitives['rpm_gpg_key']))
            }

        rendered: str = template.render(context)

        with TemporaryDirectory() as repo_directory:
            with NamedTemporaryFile() as repo_configuration:
                repo_configuration.write(rendered.encode())
                repo_configuration.flush()

                output: bytes = subprocess.check_output([
                    'yum',
                    '--disableplugin=*',
                    '--installroot', repo_directory,
                    '-c', repo_configuration.name,
                    '--disablerepo=*',
                    '--enablerepo=temp',
                    'info', self.release_package
                ])

                if b'Release' in output:
                    for line in output.split(b'\n'):
                        if line.startswith(b'Version'):
                            version: list = line.split(b'Version     : ')[1].split(b'.')
                            major: int = int(version[0])
                            minor: int = int(version[1])
                            self.major: int = major
                            self.minor: int = minor
                            break
                else:
                    raise RuntimeError('Could not update OS version')
