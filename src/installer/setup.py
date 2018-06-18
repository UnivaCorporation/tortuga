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

    result += list_files(Path('alembic'))
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
        'celery==4.1.0',
        'cryptography',
        #
        # Normally, kombu is installed as a dependency of celery, however
        # we need to pin it to 4.1.0 as we are seeing problems with 4.2.0
        #
        'kombu==4.1.0',
        'tortuga-core',
        'Jinja2',
        'CherryPy==15.0.0',
        'PyYAML',
        'SQLAlchemy',
        'Routes',
        'six',
        'pyjwt',
        'pyzmq',
        'redis',
        'gevent<1.3.2',
        'marshmallow-sqlalchemy',
        'alembic',
        'websockets',
    ],
    namespace_packages=['tortuga'],
    entry_points={
        'console_scripts': [
            'tortugawsd=tortuga.web_service.main:main',
            'add-nic=tortuga.scripts.add_nic:main',
            'delete-nic=tortuga.scripts.delete_nic:main',
            'genconfig=tortuga.scripts.genconfig:main',
            'get-nodes-with-component=tortuga.scripts.get_nodes_with_component:main',
            'get-swprofile-nodes=tortuga.scripts.get_swprofile_nodes:main',
            'get-tortuga-node=tortuga.scripts.get_tortuga_node:main',
            'get-usable-hardware-profile-list=tortuga.scripts.get_usable_hardware_profile_list:main',
            'get-usable-hardware-profiles=tortuga.scripts.get_usable_hardware_profiles:main',
            'get-usable-idle-nodes=tortuga.scripts.get_usable_idle_nodes:main',
            'get-usable-idle-nodes-by-low-cost=tortuga.scripts.get_usable_idle_nodes_by_low_cost:main',
            'get-usable-nodes=tortuga.scripts.get_usable_nodes:main',
            'install-kit=tortuga.scripts.install_kit:main',
            'install-os-kit=tortuga.scripts.install_os_kit:main',
            'pre-add-host=tortuga.scripts.pre_add_host:main',
            'run-post-install=tortuga.scripts.run_post_install:main',
            'set-private-dns-zone=tortuga.scripts.set_private_dns_zone:main',
            'tortuga-proxy-config=tortuga.scripts.tortuga_proxy_config:main',
            'tortuga-setup=tortuga.scripts.tortuga_setup:main',
            'update_hiera.py=tortuga.scripts.update_hiera:main',
            'make-backup=tortuga.scripts.make_backup:main',
            'restore-backup=tortuga.scripts.restore_backup:main'
        ],
    },
    cmdclass={
        'build_py': BuildPyCommand,
        'sdist': SdistCommand,
    },
)
