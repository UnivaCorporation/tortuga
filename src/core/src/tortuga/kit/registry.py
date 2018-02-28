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
import importlib
from logging import getLogger
import pkgutil

from tortuga.exceptions.kitNotFound import KitNotFound


logger = getLogger(__name__)


KIT_INSTALLER_PACKAGES = ['tortuga_kits']
KIT_INSTALLER_REGISTRY = {}


def discover_kit_installers():
    """
    Searches for kits in KITS_PACKAGES.

    """
    for pkg_name in KIT_INSTALLER_PACKAGES:
        discover_kit_installers_in_package(pkg_name)


def discover_kit_installers_in_package(pkg_name):
    """
    Searches pkg_name for kits, and loads/imports them if found.

    :param pkg_name: the name of the python package to search for kits.

    """
    logger.debug(
        'Searching for kit installers in package: {}'.format(pkg_name))
    try:
        pkg = importlib.import_module(pkg_name)
    except ModuleNotFoundError:
        logger.debug('Package not found: {}'.format(pkg_name))
        return
    for loader, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        if is_pkg:
            full_pkg_path = '{}.{}'.format(pkg_name, name)
            try:
                importlib.import_module('{}.kit'.format(full_pkg_path))
            except ModuleNotFoundError:
                logger.debug('Package skipped: {}'.format(full_pkg_path))


def register_kit_installer(kit_class):
    """
    Registers a kit.

    :param kit_class: a subclass of KitInstallerBase

    """
    if kit_class.spec in KIT_INSTALLER_REGISTRY.keys():
        return
    KIT_INSTALLER_REGISTRY[kit_class.spec] = kit_class
    logger.info('Kit installer registered: {}'.format(kit_class.spec))


def get_kit_installer(kit_spec):
    """
    Gets a kit installer from the registry.

    :param kit_spec:     a kit spec tuple ('name', 'version', 'iteration')
    :return:             a kit installer instance
    :raises KitNotfound:

    """
    try:
        return KIT_INSTALLER_REGISTRY[kit_spec]
    except KeyError:
        raise KitNotFound()


def get_all_kit_installers():
    """
    Gets a list of all kit installers

    :return: a list of kit installer instances

    """
    return [ki for ki in KIT_INSTALLER_REGISTRY.values()]
