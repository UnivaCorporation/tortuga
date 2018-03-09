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
from .base import RedHatFamily, RedHatFamilyPrimitives, REPO_CONFIGURATION_TEMPLATE


class CentOs6Primitives(RedHatFamilyPrimitives):
    """
    Represent locations of needed primitives
    from the CentOS 6 distributions.
    """
    def __new__(cls) -> Dict[str, str]:
        """
        :return: None
        """
        return super(CentOs6Primitives, cls).__new__(cls, rpm_gpg_key='RPM-GPG-KEY-CentOS-6')


class CentOs6(RedHatFamily):
    """
    Represents a CentOS 6 distribution.
    """
    __abstract__: bool = False

    def __init__(self, source_path: str, architecture: str = 'x86_64') -> None:
        """
        :param source_path: String local path or remote uri
        :param architecture: String targeted architecture
        :returns: None
        """
        super(CentOs6, self).__init__(
            source_path,
            'centos',
            6,
            0,
            architecture
        )

        self._primitives: CentOs6Primitives = CentOs6Primitives()

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
                    'info', 'centos-release'
                ])

                if b'Release' in output:
                    for line in output.split(b'\n'):
                        if line.startswith(b'Version'):
                            major: int = int(line.split(b'Version     : ')[1])
                            self.major: int = major
                        elif line.startswith(b'Release'):
                            minor: int = int(line.split(b'Release     : ')[1].split(b'.')[0])
                            self.minor: int = minor
                            break
                else:
                    raise RuntimeError('Could not update OS version')
