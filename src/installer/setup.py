#!/usr/bin/env python

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

# pylint: skip-file

import os
from typing import List
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
import setuptools.command.build_py
import setuptools.command.sdist

module_name = 'tortuga-installer'
maj_version = '6.3'
version = maj_version + '.0'
module_version = version


if os.getenv('BUILD_NUMBER'):
    module_version += '.dev{0}'.format(os.getenv('BUILD_NUMBER'))


def walkfiles(d):
    for f in d.iterdir():
        if f.is_dir():
            for item in walkfiles(f):
                yield item

            continue
        else:
            yield f


def list_files(srcdir: Path) -> List[str]:
    result = []

    for dirname, subdirnames, files in os.walk(str(srcdir)):
        if files:
            result.append((dirname, [str(Path(dirname) / fn) for fn in files]))

    return result


def get_files():
    result = []

    result += list_files(Path('etc'))
    result += list_files(Path('share'))
    result += list_files(Path('config'))

    result.append(
        ('share/locale/en/LC_MESSAGES', [
            'share/locale/en/LC_MESSAGES/tortugaapps.mo',
        ]))

    result += list_files(Path('man'))

    return result


def build_locale():
    cmd = ('pybabel compile -d share/locale -l en'
           ' -i share/locale/en/LC_MESSAGES/tortugaapps.po'
           ' --domain tortugaapps')

    subprocess.run(cmd, shell=True)


class CommonBuildStep:
    def pre_build(self):
        build_locale()


class BuildPyCommand(setuptools.command.build_py.build_py, CommonBuildStep):
    """
    Override 'build_py' command to generate files before build
    """

    def run(self):
        self.pre_build()

        setuptools.command.build_py.build_py.run(self)


class SdistCommand(setuptools.command.sdist.sdist, CommonBuildStep):
    def run(self):
        self.pre_build()

        setuptools.command.sdist.sdist.run(self)


setup(
    name=module_name,
    version=module_version,
    description='Tortuga installer component',
    author='Univa Corporation',
    author_email='engineering@univa.com',
    url='http://univa.com',
    license='Apache 2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    zip_safe=False,
    scripts=[str(fn) for fn in walkfiles(Path('bin'))],
    data_files=get_files(),
    install_requires=[
        'tortuga-core',
        'Jinja2',
        'CherryPy',
        'PyYAML',
        'SQLAlchemy',
        'Routes',
        'six',
        'pyzmq',
        'gevent',
        'marshmallow-sqlalchemy',
    ],
    namespace_packages=['tortuga'],
    entry_points={
        'console_scripts': [
            'tortugawsd=tortuga.web_service.main:main',
            'src/installer/bin/add-nic=tortuga.scripts.add_nic:main',
            'src/installer/bin/delete-nic=tortuga.scripts.delete_nic:main',
            'src/installer/bin/genconfig=tortuga.scripts.genconfig:main',
            'src/installer/bin/get-active-children=tortuga.scripts.get_active_children:main',
            'src/installer/bin/get-children=tortuga.scripts.get_children:main',
            'src/installer/bin/get-idle-children=tortuga.scripts.get_idle_children:main',
            'src/installer/bin/get-nodes-with-component=tortuga.scripts.get_nodes_with_component:main',
            'src/installer/bin/get-swprofile-nodes=tortuga.scripts.get_swprofile_nodes:main',
            'src/installer/bin/get-tortuga-node=tortuga.scripts.get_tortuga_node:main',
            'src/installer/bin/get-usable-hardware-profile-list=tortuga.scripts.get_usable_hardware_profile_list:main',
            'src/installer/bin/get-usable-hardware-profiles=tortuga.scripts.get_usable_hardware_profiles:main',
            'src/installer/bin/get-usable-idle-nodes=tortuga.scripts.get_usable_idle_nodes:main',
            'src/installer/bin/get-usable-idle-nodes-by-low-cost=tortuga.scripts.get_usable_idle_nodes_by_low_cost:main',
            'src/installer/bin/get-usable-nodes=tortuga.scripts.get_usable_nodes:main',
            'src/installer/bin/install-kit=tortuga.scripts.install_kit:main',
            'src/installer/bin/install-os-kit=tortuga.scripts.install_os_kit:main',
            'src/installer/bin/pre-add-host=tortuga.scripts.pre_add_host:main',
            'src/installer/bin/run-post-install=tortuga.scripts.run_post_install:main',
            'src/installer/bin/set-parent-node=tortuga.scripts.set_parent_node:main',
            'src/installer/bin/set-private-dns-zone=tortuga.scripts.set_private_dns_zone:main',
            'src/installer/bin/tortuga-proxy-config=tortuga.scripts.tortuga_proxy_config:main',
            'src/installer/bin/tortuga-setup=tortuga.scripts.tortuga_setup:main',
            'src/installer/bin/update_hiera.py=tortuga.scripts.update_hiera:main',
        ],
    },
    cmdclass={
        'build_py': BuildPyCommand,
        'sdist': SdistCommand,
    },
)
