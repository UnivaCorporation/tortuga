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

import configparser
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, List

from tortuga.boot.distro import DistributionFactory
from tortuga.config.configManager import ConfigManager
from tortuga.db import componentDbApi
from tortuga.db.dbManager import DbManager
from tortuga.db.kitDbApi import KitDbApi
from tortuga.exceptions.eulaAcceptanceRequired import EulaAcceptanceRequired
from tortuga.exceptions.kitAlreadyExists import KitAlreadyExists
from tortuga.exceptions.kitInstallError import KitInstallError
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.osNotSupported import OsNotSupported
from tortuga.exceptions.softwareProfileComponentAlreadyExists import \
    SoftwareProfileComponentAlreadyExists
from tortuga.exceptions.unrecognizedKitMedia import UnrecognizedKitMedia
from tortuga.helper import osHelper
from tortuga.kit import utils
from tortuga.kit.mountManager import MountManager
from tortuga.kit.utils import format_kit_descriptor
from tortuga.objects.component import Component
from tortuga.objects.kit import Kit
from tortuga.objects.osInfo import OsInfo
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.os_utility.osUtility import getOsObjectFactory, mapOsName
from tortuga.repo import repoManager
from tortuga.softwareprofile import softwareProfileFactory
from tortuga.types import Singleton
from tortuga.utility.actionManager import ActionManager

from .eula import BaseEulaValidator
from .loader import load_kits
from .registry import get_kit_installer


class KitManager(TortugaObjectManager, Singleton):
    def __init__(self, eula_validator=None):
        super(KitManager, self).__init__()

        self._eula_validator = eula_validator
        if not self._eula_validator:
            self._eula_validator = BaseEulaValidator()

        self._kit_db_api = KitDbApi()
        self._config_manager = ConfigManager()
        self._kits_root = self._config_manager.getKitDir()
        self._component_db_api = componentDbApi.ComponentDbApi()

    def getKitList(self):
        """
        Get all installed kits.

        """
        return self._kit_db_api.getKitList()

    def getKit(self, name, version=None, iteration=None):
        """
        Get a single kit by name, and optionally version and/or iteration.

        :param name:      the kit name
        :param version:   the kit version
        :param iteration: the kit iteration
        :return:          the kit instance

        """
        return self._kit_db_api.getKit(name, version, iteration)

    def getKitById(self, id_):
        """
        Get a single kit by id.

        :param id_: the kit id
        :return:    the kit instance

        """
        return self._kit_db_api.getKitById(id_)

    def get_kit_url(self, name, version, iteration):
        kit = Kit(name, version, iteration)
        native_repo = repoManager.getRepo()
        return os.path.join(
            native_repo.getRemoteUrl(), kit.getTarBz2FileName())

    def installKit(self, name, version, iteration, key=None):
        """
        Install kit using kit name/version/iteration.

        The kit package must be located in the remote repository for the
        native OS.

        Kit will be installed for all operating systems that:
            1) have repo configured on the local machine
            2) are specified in the kit.xml file

        Raises:
            KitAlreadyExists
        """

        kit = Kit(name, version, iteration)

        # nativeRepo = repoManager.getRepo()
        kitPkgUrl = self.get_kit_url(name, version, iteration)

        # Check for kit existence.
        self._check_if_kit_exists(kit)

        self.getLogger().debug(
            '[{0}] Installing kit [{1}]'.format(
                self.__class__.__name__, kit))

        return self.installKitPackage(kitPkgUrl, key)

    def installKitPackage(self, kit_pkg_url, key=None):
        """
        Install kit from the given kit url (url might be a local file). Kit
        will be installed for all operating systems that:

            1) have repo configured on the local machine
            2) are specified in the kit.xml file

        :raisesKitAlreadyExists:
        :raisesEulaAcceptanceRequired:

        """
        self.getLogger().debug('Installing kit package:'.format(kit_pkg_url))

        #
        # Download/copy and unpack kit archive.
        #
        kit_src_path = os.path.basename(kit_pkg_url)
        kit_pkg_path = utils.retrieve(
            kit_src_path, kit_pkg_url, self._kits_root)
        kit_spec = utils.unpack_archive(kit_pkg_path, self._kits_root)

        #
        # Load and initialize kit installer
        #
        load_kits()
        installer = get_kit_installer(kit_spec)()

        if not installer.is_installable():
            self.getLogger().warning(
                'Kit is not installable: {}'.format(kit_spec))
            return

        kit = installer.get_kit()

        #
        # This method will throw KitAlreadyExists, if it does...
        #
        self._check_if_kit_exists(kit)

        #
        # Validate eula
        #
        eula = installer.get_eula()
        if not eula:
            self.getLogger().debug('No EULA acceptance required')
        else:
            if not self._eula_validator.validate_eula(eula):
                raise EulaAcceptanceRequired(
                    'You must accept the EULA to install this kit')

        #
        # Runs the kit pre install method
        #
        installer.run_action('pre_install')

        #
        # Get list of operating systems supported by this installer
        #
        os_info_list = [
            repo.getOsInfo() for repo in repoManager.getRepoList()
        ]

        #
        # Install operating system specific packages
        #
        self._install_os_packages(kit, os_info_list)

        #
        # Initialize andy DB tables provided by the kit
        #
        db_manager = DbManager()
        db_manager.init_database()

        #
        # Add the kit to the database
        #
        self._kit_db_api.addKit(kit)

        #
        # Clean up the kit archive directory
        #
        self._clean_kit_achiv_dir(kit, installer.install_path)

        #
        # Install puppet modules
        #
        installer.run_action('install_puppet_modules')

        #
        # Run post install
        #
        try:
            installer.run_action('post_install')
        except Exception as e:
            self._uninstall_kit(kit, True)
            raise KitInstallError(
                'Kit installation failed during post_install: {}'.format(e))

        if eula:
            ActionManager().logAction(
                'Kit [{}] installed and EULA accepted at [{}]'
                ' local machine time.'.format(
                    installer.spec, time.ctime())
            )
        else:
            ActionManager().logAction(
                'Kit [{}] installed at [{}] local machine time.'.format(
                    installer.spec, time.ctime())
            )

        return kit

    def _check_if_kit_exists(self, kit):
        """
        Check if a kit exists, if it does then raise an exception.

        :raisesKitAlreadyExists:

        """
        try:
            self._kit_db_api.getKit(kit.getName(), kit.getVersion(),
                                    kit.getIteration())
            raise KitAlreadyExists(
                'Kit already exists: ({}, {}, {})'.format(
                    kit.getName(), kit.getVersion(), kit.getIteration()
                )
            )
        except KitNotFound:
            pass

    def _install_os_packages(self, kit, os_info_list):
        """
        Installs OS specific packages from the kit into the repo.

        :param kit:          the kit instance
        :param os_info_list: a list of osInfo instances to install for

        """
        all_component_list = kit.getComponentList()

        for os_info in os_info_list:
            self.getLogger().debug(
                'Preparing to install ({}, {}, {}) for {}'.format(
                    kit.getName(), kit.getVersion(), kit.getIteration(),
                    os_info
                )
            )

            #
            # Get list of compatible components
            #
            os_object_factory = getOsObjectFactory(
                mapOsName(os_info.getName())
            )
            component_manager = os_object_factory.getComponentManager()
            component_list = component_manager.getCompatibleComponentList(
                os_info, all_component_list)
            if not component_list:
                continue

            #
            # Create the package directory in the repo
            #
            repo = repoManager.getRepo(os_info)
            full_dir = os.path.join(repo.getLocalPath(), kit.getKitRepoDir())
            osUtility.createDir(full_dir)

            #
            # Install the packages into the repo package directory
            #
            for component in component_list:
                self.getLogger().debug(
                    '[{0}] Found component [{1}]'.format(
                        self.__class__.__name__, component))

                for package in component.getPackageList():
                    package_file = os.path.join(
                        kit.install_path, package.getRelativePath())
                    self.getLogger().debug(
                        '[{0}] Found package [{1}]'.format(
                            self.__class__.__name__, package_file))
                    repo.addPackage(package_file, kit.getKitRepoDir())
            repo.create(kit.getKitRepoDir())

    def get_kit_eula(self, name, version, iteration=None):
        return self.get_kit_package_eula(
            self.get_kit_url(name, version, iteration)
        )

    def get_kit_package_eula(self, kit_pkg_url):
        #
        # Download/copy and unpack kit archive.
        #
        kit_src_path = os.path.basename(kit_pkg_url)
        kit_pkg_path = utils.retrieve(
            kit_src_path, kit_pkg_url, self._kits_root)
        kit_spec = utils.unpack_archive(kit_pkg_path, self._kits_root)

        #
        # Get the EULA from the installer
        #
        load_kits()
        installer = get_kit_installer(kit_spec)()
        eula = installer.get_eula()

        return eula

    def _retrieveOSMedia(self, url: str) -> str:
        """
        Download the OS media.

        :param url: String
        :return: String file path to download
        """
        return urllib.request.urlretrieve(url)[0]

    def _processMediaspec(self, os_media_urls: List[str]) -> List[dict]:
        """
        :param os_media_urls: List String
        :return: List Dictionary

        """
        media_list: List[dict] = []

        for url in os_media_urls:
            m = urllib.parse.urlparse(url)

            media_item_dict = {
                'urlparse': m,
            }

            if m.scheme.lower() in ('http', 'https') and \
                    os.path.splitext(m.path)[1].lower() == '.iso':
                file_name = self._retrieveOSMedia(m.geturl())

                media_item_dict['localFilePath'] = file_name

            media_list.append(media_item_dict)

        return media_list

    @staticmethod
    def _getKitOpsClass(os_family_info) -> Any:
        """
        Import the KitOps class for the specified OS family name

        Raises:
            OsNotSupported
        """
        try:
            _temp = __import__(
                'tortuga.kit.%sOsKitOps' % os_family_info.getName(),
                globals(),
                locals(),
                ['KitOps'],
                0
            )

            return getattr(_temp, 'KitOps')
        except ImportError:
            raise OsNotSupported('Currently unsupported distribution')

    def _checkExistingKit(self, kitname, kitversion, kitarch):
        """
        Raises:
            KitAlreadyExists
        """

        try:
            kit = self._kit_db_api.getKit(kitname, kitversion)

            longname = format_kit_descriptor(kitname, kitversion, kitarch)

            # Attempt to get matching OS component
            for c in kit.getComponentList():
                if c.getName() != longname:
                    continue

                for cOs in c.getOsInfoList():
                    if cOs == OsInfo(kitname, kitversion, kitarch):
                        raise KitAlreadyExists(
                            "OS kit [%s] already installed" % longname)

            # Kit exists, but doesn't have a matching os component
        except KitNotFound:
            pass

    def _create_kit_db_entry(self, kit):
        """
        Creates a database entry for a kit.

        :param kit:
        :return: a Kit instance (TortugaObject)

        """
        try:
            return self._kit_db_api.getKit(kit['name'], kit['ver'])
        except KitNotFound:
            pass

        # Add the database entries for the kit
        kitObj = Kit(name=kit['name'], version=kit['ver'], iteration='0')
        kitObj.setDescription(kit['sum'])
        kitObj.setIsOs(True)
        kitObj.setIsRemovable(True)

        kit_descr = format_kit_descriptor(kit['name'], kit['ver'], kit['arch'])

        newComp = Component(name=kit_descr, version=kit['ver'])

        newComp.setDescription('%s mock component' % (kit_descr))

        newComp.addOsInfo(
            osHelper.getOsInfo(kit['name'], kit['ver'], kit['arch']))

        kitObj.addComponent(newComp)

        # Kit does not previously exist, perform 'normal' add kit operation
        self._kit_db_api.addKit(kitObj)

        return kitObj

    def installOsKit(self, os_media_urls: List[str], **kwargs):
        """

        :param os_media_urls:
        :param kwargs:
        :return:
        """
        media_list: List[dict] = self._processMediaspec(os_media_urls)

        os_distro = None
        kit_ops = None
        enable_proxy = False
        mount_manager = None

        is_interactive = kwargs['bInteractive'] \
            if 'bInteractive' in kwargs else False

        use_symlinks = kwargs['bUseSymlinks'] \
            if 'bUseSymlinks' in kwargs else False

        # If 'mirror' is True, treat 'mediaspec' as a mirror, instead of
        # specific OS version. This affects the stored OS version.
        is_mirror = kwargs['mirror'] if 'mirror' in kwargs else False

        media: dict = media_list[0]  # For now, remove support for multiple ISOs / mirrors.
        source_path = None
        mount_manager_source_path = None

        try:
            if use_symlinks:
                source_path = media['urlparse'].path
            elif 'localFilePath' in media:
                # Remote ISO file has been transferred locally and
                # filename is stored in 'localFilePath'

                mount_manager_source_path = media['localFilePath']
            else:
                pr = media['urlparse']

                if pr.scheme.lower() in ('http', 'https'):
                    # This is a proxy URL
                    source_path = pr.geturl()

                    enable_proxy = True
                elif not pr.scheme or pr.scheme.lower() == 'file':
                    if os.path.ismount(pr.path):
                        # Mount point specified
                        source_path = pr.path
                    else:
                        mount_manager_source_path = pr.path
                else:
                    raise UnrecognizedKitMedia(
                        'Unhandled URL scheme [%s]' % pr.scheme)

            # Mount source media, as necessary
            if mount_manager_source_path:
                mount_manager = MountManager(mount_manager_source_path)
                mount_manager.mountMedia()

                source_path = mount_manager.mountpoint

            if os_distro is None:
                # Determine the OS we're working with...
                os_distro = DistributionFactory(source_path)()
                if os_distro is None:
                    raise OsNotSupported('Could not match media')

                os_info = os_distro.get_os_info()

                # Check if OS is already installed before attempting to
                # perform copy operation...
                try:
                    self._checkExistingKit(
                        os_info.getName(),
                        os_info.getVersion(),
                        os_info.getArch())
                except KitAlreadyExists:
                    if mount_manager_source_path:
                        mount_manager.unmountMedia()

                        if 'localFilePath' in media:
                            if os.path.exists(
                                    media['localFilePath']):
                                os.unlink(media['localFilePath'])

                    raise

                kit_ops_class = self._getKitOpsClass(
                    os_info.getOsFamilyInfo())

                kit_ops = kit_ops_class(
                    os_distro, bUseSymlinks=use_symlinks, mirror=is_mirror)

                kit = kit_ops.prepareOSKit()

            # Copy files here
            if enable_proxy:
                kit_ops.addProxy(source_path)
            else:
                descr = None

                if is_interactive:
                    descr = "Installing..."

                kit_ops.copyOsMedia(descr=descr)
        finally:
            if mount_manager_source_path:
                # MountManager instance exists.  Unmount any mounted
                # path
                mount_manager.unmountMedia()

                if 'localFilePath' in media:
                    if os.path.exists(media['localFilePath']):
                        os.unlink(media['localFilePath'])

        kit_object = self._create_kit_db_entry(kit)

        self._postInstallOsKit(kit_object)

        return kit_object

    def _postInstallOsKit(self, kit):
        """
        Enable the OS component that may already be associated with an
        existing software profile.  This is possible when OS media is
        not available during installation/creation of software profiles
        """
        swProfileApi = softwareProfileFactory.getSoftwareProfileApi()

        osComponents = kit.getComponentList()
        kitOsInfo = osComponents[0].getOsComponentList()[0].getOsInfo()

        # Load the newly added kit component from the database
        c = self._component_db_api.getComponent(osComponents[0].getName(),
                                                osComponents[0].getVersion(),
                                                kitOsInfo)

        # Iterate over all software profiles looking for matching OS
        for swProfile in swProfileApi.getSoftwareProfileList():
            if swProfile.getOsInfo() != kitOsInfo:
                continue

            # Ensure OS component is enabled on this software profile
            try:
                self._component_db_api.addComponentToSoftwareProfile(
                    c.getId(), swProfile.getId())
            except SoftwareProfileComponentAlreadyExists:
                # Not an error...
                pass

    def _clean_kit_achiv_dir(self, kit, kit_dir):
        """
        Remove packages from the kit archive directory

        """
        component_list = kit.getComponentList()
        if not component_list:
            self.getLogger().debug('No components found')
            return

        for component in component_list:
            self.getLogger().debug(
                'Found component: {}'.format(component))

            for package in component.getPackageList():
                package_path = os.path.join(kit_dir,
                                            package.getRelativePath())

                if os.path.exists(package_path):
                    self.getLogger().debug(
                        'Deleting package: {}'.format(package_path))
                    os.remove(package_path)
                else:
                    self.getLogger().debug(
                        'Skipping non-existent package: {}'.format(
                            package_path))

    def deleteKit(self, name, version=None, iteration=None, force=False):
        """
        Delete a kit.

        :param name:      the kit name
        :param version:   the kit version
        :param iteration: the kit iteration
        :param force:     whether or not to force the deletion

        """
        kit = self.getKit(name, version, iteration)
        if kit.getIsOs():
            self._delete_os_kit(kit, force)
        else:
            self._delete_kit(kit, force)

        self.getLogger().info('Deleted kit: {}'.format(kit))

    def _delete_kit(self, kit, force):
        """
        Deletes a regular kit.

        :param kit:   the Kit instance
        :param force: whether or not to force the deletion

        """
        kit_install_path = os.path.join(self._kits_root, kit.getDirName())
        if os.path.exists(kit_install_path):
            kit_spec = (kit.getName(), kit.getVersion(), kit.getIteration())

            load_kits()
            installer = get_kit_installer(kit_spec)()

            installer.run_action('pre_uninstall')
            self._uninstall_kit(kit, force)
            installer.run_action('uninstall_puppet_modules')
            installer.run_action('post_uninstall')

    def _delete_os_kit(self, kit, force):
        """
        Deletes an OS kit.

        :param kit:   the Kit instance
        :param force: whether or not to force the deletion

        """
        osi = kit.getComponentList()[0].getOsInfoList()[0]
        repo_dir = os.path.join(kit.getName(), kit.getVersion(),
                                osi.getArch())
        self._uninstall_kit(kit, force)

    def _uninstall_kit(self, kit, force):
        """
        Uninstalls the kit and it's file repos.

        :param kit:      the Kit instance
        :param force:    whether or not to force the deletion

        """
        repo_dir = kit.getKitRepoDir()

        #
        # Remove the kit from the DB
        #
        self._kit_db_api.deleteKit(kit.getName(), kit.getVersion(),
                                   kit.getIteration(), force=force)

        #
        # Remove the files and repo
        #
        for repo in repoManager.getRepoList():
            #
            # Delete the repo
            #
            repo.delete(repo_dir)

            #
            # Remove repo files
            #
            full_repo_dir = os.path.join(repo.getLocalPath(), repo_dir)
            self.getLogger().debug(
                'Removing repo dir: {}'.format(full_repo_dir))
            #
            # When LINKOSKITMEDIA is used, the kit directory is a symlink
            # to the real media, delete the link instead of attempting
            # to delete the directory.
            #
            if os.path.islink(full_repo_dir):
                os.unlink(full_repo_dir)
            else:
                osUtility.removeDir(full_repo_dir)

        #
        # Check and clean up proxy
        #
        self.remove_proxy(repo_dir)

        #
        # Remove the kit archive dir
        #
        kit_arch_dir = os.path.join(repoManager.getKitArchiveDir(),
                                    kit.getDirName())
        if os.path.exists(kit_arch_dir):
            self.getLogger().debug(
                'Removing kit archive dir: {}'.format(kit_arch_dir))
            osUtility.removeDir(kit_arch_dir)

    def remove_proxy(self, repoDir):
        # Check for this repo as an actual entry in the tortuga apache.conf
        # file to remove

        config = configparser.ConfigParser()

        cfgfile = os.path.join(
            self._config_manager.getKitConfigBase(),
            'base/apache-component.conf'
        )

        config.read(cfgfile)

        paths = config.get('cache', 'cache_path_list').split()

        newPaths = paths[:]

        for p in paths:
            if p.endswith(repoDir):
                # Remove this dir from the cache
                newPaths.remove(p)

        if config.has_option('proxy', 'proxy_list'):
            proxies = config.get('proxy', 'proxy_list').split()

            if repoDir in ' '.join(proxies):
                # Remove this repository from the proxy
                for entry in proxies[:]:
                    if repoDir in entry:
                        config.remove_option('proxy', entry)
                        proxies.remove(entry)
        else:
            proxies = []

        # Update apache configuration
        config.set('cache', 'cache_path_list', '\n'.join(newPaths))
        config.set('proxy', 'proxy_list', ' '.join(proxies))

        with open(cfgfile, 'w') as fp:
            config.write(fp)

    def configureProxy(self, medialoc, repoDir):
        config = configparser.ConfigParser()

        cfgfile = os.path.join(
            self._config_manager.getKitConfigBase(), 'base/apache-component.conf')

        config.read(cfgfile)

        proxies = []

        paths = []

        if config.has_section('cache') and \
                config.has_option('cache', 'cache_path_list'):
            paths = config.get('cache', 'cache_path_list').split()

        if repoDir not in paths:
            paths.append(repoDir)

        if not config.has_section('cache'):
            config.add_section('cache')

        config.set('cache', 'cache_path_list', '\n'.join(paths))

        if config.has_section('proxy') and \
                config.has_option('proxy', 'proxy_list'):
            proxies = config.get('proxy', 'proxy_list').split()

        if repoDir not in proxies:
            proxies.append(repoDir)

        if not config.has_section('proxy'):
            config.add_section('proxy')

        config.set('proxy', 'proxy_list', ' '.join(proxies))
        config.set('proxy', repoDir, medialoc)

        with open(cfgfile, 'w') as fp:
            config.write(fp)
