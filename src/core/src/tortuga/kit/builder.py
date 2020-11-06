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

import copy
import json
import logging
import os
from pathlib import Path
import shutil

from tortuga.config import version_is_compatible, VERSION
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.kitBuildError import KitBuildError
from tortuga.logging import KIT_NAMESPACE
from tortuga.os_utility.tortugaSubprocess import executeCommand

from .metadata import KitMetadataSchema


logger = logging.getLogger(KIT_NAMESPACE)


KIT_METADATA_FILE = 'kit.json'
KIT_PACKAGE_NAME = 'tortuga_kits'

SRC_DIR = 'src'
BUILD_DIR = 'build'
DIST_DIR = 'dist'

DEFAULT_INCLUDE_FILES = [
    'python_packages',
    'bin',
    'doc',
    'README.*'
]

DEFAULT_EXCLUDE_FILES = [
    '.pyc',
    '__pycache__',
    '.svn',
    '.gitignore',
    '.cvsignore',
    'puppet_modules',
    '.mypy_cache',
    '.pytest_cache',
    '.gitlab-ci.yml',
]


class KitBuilder(object):
    def __init__(self, working_directory: str = None, version: str = None,
                 ignore_directory_version: bool = False):
        """
        Initialization.

        :param str working_directory:         the working directory in which
                                              the build process will be run.
        :param str version:                   override the version number in
                                              the kit.json file in the form
                                              of x.y.z
        :param bool ignore_directory_version: don't move tortuga_kits/kitname
                                              to tortuga_kits/kitname_x_y_z

        """
        if working_directory:
            os.chdir(working_directory)

        self._third_party_path = os.getenv('THIRD_PARTY')

        self._kit_meta = KitBuilder.get_kit_metadata(version)

        self._kit_descriptor = 'kit-{}-{}-{}'.format(
            self._kit_meta['name'],
            self._kit_meta['version'],
            self._kit_meta['iteration']
        )

        self._kit_src_dir = self._get_kit_src_dir()
        if ignore_directory_version:
            self._kit_dest_dir = self._kit_src_dir

        else:
            self._kit_dest_dir = '{}_{}'.format(
                self._kit_meta['name'],
                self._kit_meta['version'].replace('.', '_')
            )

        self._include_files = copy.copy(DEFAULT_INCLUDE_FILES)
        self._include_files.extend(self._kit_meta.get('include_files', []))

        self._exclude_files = copy.copy(DEFAULT_EXCLUDE_FILES)
        self._exclude_files.extend(self._kit_meta.get('exclude_files', []))

        self._src_makefile_found = False
        self._discover_src_makefile()

        self._python_setup_found = False
        self._discover_python_setup()

        self._puppet_modules = []
        self._discover_puppet_modules()

    @staticmethod
    def get_kit_metadata(version: str = None):
        """
        Gets kit metadata from the KIT_METADATA_FILE, validates it, and
        returns the result as a python dict.

        :param str version: override the version string

        :return: dict of the loaded metadata

        """
        logger.info('Getting kit metadata...')

        if not os.path.exists(KIT_METADATA_FILE):
            raise KitBuildError(
                'No kit metadata file found: {}'.format(KIT_METADATA_FILE))

        kit_meta_fp = open(KIT_METADATA_FILE)
        kit_meta = json.load(kit_meta_fp)

        if version:
            kit_meta['version'] = version

        errors = KitMetadataSchema().validate(kit_meta)
        if errors:
            raise KitBuildError(
                'Kit metadata validation error: {}'.format(errors))

        requires_core = kit_meta.get('requires_core', VERSION)
        if not version_is_compatible(requires_core):
            raise KitBuildError(
                'The {} kit requires tortuga core >= {}'.format(
                    kit_meta['name'],
                    requires_core
                )
            )

        return kit_meta

    def _get_kit_src_dir(self):
        """
        Gets the source directory for the kit.

        :return str: the source directory name for the kit

        """
        tortuga_kits_dir = Path('./{}'.format(KIT_PACKAGE_NAME))

        dir_list = [
            x for x in tortuga_kits_dir.iterdir()
            if x.is_dir() and not x.name.startswith('.')
        ]

        if len(dir_list) > 1:
            raise KitBuildError(
                'Multiple sub-directories found under tortuga_kits')

        if len(dir_list) == 0:
            raise KitBuildError(
                'No sub-directories found under tortuga_kits')

        return dir_list[0].name

    def _discover_src_makefile(self):
        """
        Checks for the existence of src/Makefile

        """
        logger.info('Discovering src/Makefile...')

        if not os.path.exists(SRC_DIR):
            logger.info('No src directory found')
            return

        if not os.path.exists(os.path.join(SRC_DIR, 'Makefile')):
            logger.info('No Makefile found')
            return

        logger.info('src/Makefile found')

        self._src_makefile_found = True

    def _discover_python_setup(self):
        """
        Checks for the existence of a python setup.py file.

        """
        logger.info('Discovering setup.py...')

        if not os.path.exists('setup.py'):
            logger.info('No python setup.py found')
            return

        logger.info('Python setup.py found')

        self._python_setup_found = True

    def _discover_puppet_modules(self):
        """
        Looks for puppet modules in the kit directory.

        """
        logger.info('Discovering puppet modules...')

        puppet_modules_path = os.path.join(KIT_PACKAGE_NAME,
                                           self._kit_src_dir,
                                           'puppet_modules')
        logger.info('Puppet modules path: {}'.format(puppet_modules_path))
        if not os.path.exists(puppet_modules_path) or \
                not os.path.isdir(puppet_modules_path):
            return

        self._puppet_modules = []
        for base_path, directory_names, file_names in os.walk(
                puppet_modules_path):
            for directorty_name in directory_names:
                self._puppet_modules.append({
                    'name': directorty_name,
                    'path': os.path.join(base_path, directorty_name)
                })
                logger.info('Puppet module found: {}'.format(directorty_name))
            break

        if not self._puppet_modules:
            logger.info('No puppet modules found')

    def _run_command(self, command):
        """
        Runs an external command.

        :param command:        string the command to run
        :raises KitBuildError: if the command failed

        """
        logger.info('    {}'.format(command))

        try:
            executeCommand(command)
        except CommandFailed as e:
            raise KitBuildError(str(e))

    def _copy_file(self, src_path, dst_path, excludes=None):
        """
        Copies a file.

        :param src_path:       the src_path to copy from
        :param dst_path:       the destination to copy to
        :param excludes:       list of file patterns to exclude in the copy
        :raises KitBuildError: something bad happened with rsync

        """
        logger.info('{} -> {}'.format(src_path, dst_path))

        if excludes is None:
            excludes = self._exclude_files
        exclude_params = ''
        if excludes:
            for exclude in excludes:
                exclude_params += ' --exclude {}'.format(exclude)

        cmd = 'rsync -a {} {}{}'.format(src_path, dst_path, exclude_params)
        self._run_command(cmd)

    def build(self):
        """
        Builds the current kit.

        :raises KitBuildError:

        """
        #
        # Create build directory
        #
        kit_build_dir = os.path.join(BUILD_DIR, self._kit_descriptor)
        if not os.path.isdir(kit_build_dir):
            logger.info('Creating build directory: {}'.format(kit_build_dir))
            os.makedirs(kit_build_dir)

        #
        # Create dist directory
        #
        dist_dir = DIST_DIR
        if not os.path.isdir(dist_dir):
            logger.info('Creating dist directory: {}'.format(
                dist_dir))
            os.makedirs(dist_dir)

        #
        # Build src directory
        #
        self._build_src()

        #
        # Write the metadata file
        #
        with open(os.path.join(kit_build_dir, KIT_METADATA_FILE), 'w') as mfp:
            json.dump(self._kit_meta, mfp)

        #
        # Copy the kit source directory
        #
        build_kit_src_dir = os.path.join(KIT_PACKAGE_NAME, self._kit_src_dir)
        build_kit_dest_dir = os.path.join(kit_build_dir, KIT_PACKAGE_NAME,
                                          self._kit_dest_dir)
        os.makedirs(build_kit_dest_dir, exist_ok=True)
        self._copy_file('{}/'.format(build_kit_src_dir), build_kit_dest_dir)

        #
        # Copy default kit files
        #
        logger.info('Copying kit files...')
        for file_name in self._include_files:
            if os.path.exists(file_name):
                self._copy_file(file_name, kit_build_dir)

        #
        # Build and copy puppet modules
        #
        self._build_puppet_modules()
        self._copy_puppet_modules(kit_build_dir)

        #
        # Build and copy python wheels
        #
        self._build_python_package()
        self._copy_python_package(dist_dir, kit_build_dir)

        #
        # Generate kit tarball
        #
        tarball_path = self._generate_tarball(dist_dir)
        return tarball_path

    def _build_src(self):
        """
        Builds anything in the src directory if a Makefile is found.

        """
        if not self._src_makefile_found:
            return

        logger.info('Building src...')

        cmd = '( cd {} && make && make install || /bin/true )'.format(SRC_DIR)
        self._run_command(cmd)

    def _build_python_package(self):
        """
        Builds the python package/wheel if a setup.py is found.

        """
        if not self._python_setup_found:
            return

        logger.info('Building python package...')

        cmd = 'python setup.py bdist_wheel'
        self._run_command(cmd)

    def _build_puppet_modules(self):
        """
        Builds all discovered puppet modules.

        """
        if not self._puppet_modules:
            return

        logger.info('Building puppet modules...')

        for puppet_module in self._puppet_modules:
            if os.environ.get('TORTUGA_BUILD_DOCKER'):
                target_path = os.path.join(os.environ.get('PWD'), puppet_module['path'])
                cmd = 'docker run --rm=true -v {}:/root puppet/puppet-agent module build /root'.format(
                    target_path
                )

            else:
                target_path = puppet_module['path']
                cmd = 'cd {} && /opt/puppetlabs/pdk/bin/pdk build --force'.format(target_path)
            # Copy kit.json file in for future reference
            self._copy_file(KIT_METADATA_FILE, '{}/{}'.format(target_path, KIT_METADATA_FILE))
            self._run_command(cmd)

    def _copy_python_package(self, dist_dir, kit_build_dir):
        """
        Copies the python wheel to the kit build directory.

        :param dist_dir:      the dist directory where the python wheel is
                              found
        :param kit_build_dir: the kit build directory

        """
        if not self._python_setup_found:
            return

        logger.info('Copying python package...')

        python_whl_src_path = os.path.join(
            dist_dir,
            '*.whl'
        )
        python_whl_dest_path = os.path.join(
            kit_build_dir,
            'python_packages'
        )

        if not os.path.exists(python_whl_dest_path):
            os.mkdir(python_whl_dest_path)

        self._copy_file(python_whl_src_path, python_whl_dest_path)

    def _copy_puppet_modules(self, kit_build_dir):
        """
        Copies all puppet modules that were successfully built to the
        kit build directory.

        :param kit_build_dir: string the kit build directory root

        """
        if not self._puppet_modules:
            return

        logger.info('Copying puppet modules...')

        puppet_pkg_dest_path = os.path.join(
            kit_build_dir,
            KIT_PACKAGE_NAME,
            self._kit_dest_dir,
            'puppet_modules'
        )

        if not os.path.exists(puppet_pkg_dest_path):
            os.mkdir(puppet_pkg_dest_path)

        for puppet_module in self._puppet_modules:
            puppet_pkg_path = os.path.join(
                puppet_module['path'],
                'pkg',
                '*.tar.gz'
            )
            self._copy_file(puppet_pkg_path, puppet_pkg_dest_path)

    def _generate_tarball(self, dist_dir) -> str:
        """
        Generates a tarball of the kit.

        :param dist_dir: the dist directory in which the tarball will be
                         created
        :return str: the path to the generated tarball

        """
        logger.info('Generating kit tarball...')

        tarball_file_name = '{}.tar.bz2'.format(self._kit_descriptor)
        tarball_path = os.path.abspath(
            os.path.join(dist_dir, tarball_file_name))

        logger.info('Tarball path: {}'.format(tarball_path))

        cmd = 'tar -C {} -cjvf {} {}'.format(
            BUILD_DIR,
            tarball_path,
            self._kit_descriptor
        )
        self._run_command(cmd)

        return tarball_path

    def clean(self):
        """
        Removes all build and dist files for the current kit.

        """
        if os.path.exists(BUILD_DIR):
            logger.info('Removing build directory: {}'.format(BUILD_DIR))
            shutil.rmtree(BUILD_DIR)

        if os.path.exists(DIST_DIR):
            logger.info('Removing dist directory: {}'.format(DIST_DIR))
            shutil.rmtree(DIST_DIR)

        for puppet_module in self._puppet_modules:
            puppet_pkg_path = os.path.join(
                puppet_module['path'],
                'pkg'
            )
            if os.path.exists(puppet_pkg_path):
                logger.info('Removing puppet build directory: {}'.format(
                    puppet_pkg_path))
                shutil.rmtree(puppet_pkg_path)

        if self._python_setup_found:
            logger.info('Removing python egg-info directory')
            cmd = 'rm -rf $(find . -type d -name \\*.egg-info)'
            self._run_command(cmd)

        if self._src_makefile_found:
            logger.info('Running make clean on src')
            cmd = 'cd {} && make clean'.format(SRC_DIR)
            self._run_command(cmd)
