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
import copy
import importlib
import inspect
import json
import os
import pkgutil
from logging import getLogger
from typing import Optional, Type

from tortuga.config import VERSION, version_is_compatible
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.kit.metadata import KIT_METADATA_FILE, KitMetadataSchema
from tortuga.objects.component import Component
from tortuga.objects.eula import Eula
from tortuga.objects.kit import Kit
from tortuga.objects.osFamilyInfo import OsFamilyInfo
from tortuga.os_utility.tortugaSubprocess import executeCommand

from .registry import register_kit_installer
from .utils import pip_install_requirements


logger = getLogger(__name__)


EULA_FILE = 'docs/EULA.txt'


class ConfigurableMixin:
    """
    A mixin class for configurable entities.

    """
    config_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_parser = None
        self.config_path = os.path.join(self.get_config_base(), self.name)
        self.config_file = os.path.join(
            self.config_path,
            '{}-{}.conf'.format(self.name, self.config_type)
        )

    def get_config_base(self):
        raise NotImplementedError()

    def get_config_defaults(self):
        return {}

    def get_config(self, reread=False):
        if self._config_parser is None or reread:
            try:
                self._config_parser = configparser.ConfigParser()
                self._config_parser.read(self.config_file)
            except:
                logger.debug(
                    'No valid configuration for %s: %s',
                    self.config_type, self.name
                )
        return self._config_parser

    def set_defaults(self, config_parser):
        if config_parser is None:
            config_parser = self.get_config()

        #
        # Load defaults
        #
        defaults = self.get_config_defaults()
        defaults_config_parser = configparser.ConfigParser()
        if defaults is not None:
            for k, v in list(defaults.items()):
                if not defaults_config_parser.has_section(k):
                    defaults_config_parser.add_section(k)
                if v is not None:
                    for vk, vv in list(v.items()):
                        defaults_config_parser.set(k, vk, vv)

        #
        # Now override program defaults with existing values
        #
        for section in config_parser.sections():
            if not defaults_config_parser.has_section(section):
                defaults_config_parser.add_section(section)
            for option in config_parser.options(section):
                defaults_config_parser.set(
                    section, option, config_parser.get(section, option))

        #
        # Finally set the internal config parser to our new defaults
        #
        self._config_parser = defaults_config_parser

    def write_default_config(self):
        config_parser = configparser.ConfigParser()
        self.set_defaults(config_parser)
        self.write_config()

    def write_config(self):
        if self.config_file is None:
            return

        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        config_parser = self.get_config()
        with open(self.config_file, 'w') as fd:
            config_parser.write(fd)


class KitInstallerMeta(type):
    """
    Metaclass for kit installers.

    The purpose of this metaclass is to load the metadata from the
    KIT_METADATA_FILE file.

    """
    def __init__(cls: Type['KitInstallerBase'], name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'KitInstallerBase':
            return

        #
        # Load the kit metadata
        #
        kit_pkg_name = inspect.getmodule(cls).__package__
        kit_pkg_depth = len(kit_pkg_name.split('.'))
        kit_file_path = inspect.getfile(cls)
        kit_file_path_segments = kit_file_path.split(os.path.sep)
        kit_install_path_segments = \
            kit_file_path_segments[:-(kit_pkg_depth + 1)]
        cls.install_path = os.path.abspath(
            os.path.join(
                os.path.sep,
                *kit_install_path_segments
            )
        )

        metadata_file_path = os.path.join(cls.install_path, KIT_METADATA_FILE)
        try:
            with open(metadata_file_path) as kit_meta_fp:
                cls.load_meta(json.load(kit_meta_fp))
        except [FileNotFoundError, json.JSONDecodeError]:
            raise Exception(
                'Metadata not found for kit: {}'.format(cls.__module__))

        #
        # Register the kit class
        #
        register_kit_installer(cls)


class KitInstallerBase(ConfigurableMixin, metaclass=KitInstallerMeta):
    """
    Base class for kit installers.

    """
    config_type = 'kit'

    #
    # The kit installation directory
    #
    install_path = None

    #
    # Metadata, loaded via the load_meta class method.
    #
    name = None
    version = None
    iteration = None
    spec = (None, None, None)
    meta = {}

    #
    # Attributes, provided by instances of this class
    #
    puppet_modules = []
    task_modules = []

    def __init__(self):
        self.config_manager = ConfigManager()

        #
        # Setup paths
        #
        self.kit_path = os.path.dirname(inspect.getfile(self.__class__))
        self.puppet_modules_path = os.path.join(
            self.kit_path,
            'puppet_modules'
        )
        self.files_path = os.path.join(
            self.kit_path,
            'files'
        )

        #
        # Initialize configuration
        #
        super().__init__()

        #
        # Load components and resource adapters
        #
        self._component_installers = {}
        self._component_installers_loaded = False

        #
        # Web service controller classes
        #
        self._ws_controller_classes = []
        self._ws_controller_classes_loaded = False

        self.session = None

    def get_config_base(self):
        return self.config_manager.getKitConfigBase()

    @classmethod
    def load_meta(cls, meta_dict):
        """
        Loads the meta data for the kit into the class.

        :param meta_dict: A dict containing the metadata, as specified by
                          the KitMetadataSchema class.

        """
        errors = KitMetadataSchema().validate(meta_dict)
        if errors:
            raise Exception(
                'Kit metadata validation error: {}'.format(errors))

        requires_core = meta_dict.get('requires_core', VERSION)
        if not version_is_compatible(requires_core):
            raise Exception(
                'The {} kit requires tortuga core >= {}'.format(
                    meta_dict['name'], requires_core))

        meta_dict = copy.deepcopy(meta_dict)
        cls.name = meta_dict.pop('name')
        cls.version = meta_dict.pop('version')
        cls.iteration = meta_dict.pop('iteration')
        cls.spec = (cls.name, cls.version, cls.iteration)
        cls.meta = meta_dict

    def _load_component_installers(self):
        """
        Load component installers for this kit.

        """
        if self._component_installers_loaded:
            return

        kit_pkg_name = inspect.getmodule(self).__package__

        comp_pkg_name = '{}.components'.format(kit_pkg_name)

        logger.debug(
            'Searching for component installers in package: %s',
            comp_pkg_name
        )

        #
        # Look for the components sub-package
        #
        try:
            comp_pkg = importlib.import_module(comp_pkg_name)
        except ModuleNotFoundError:
            logger.warning(
                'No component installers found for kit: %s',
                kit_pkg_name
            )
            return

        #
        # Walk the components sub-package, looking for component installers
        #
        for loader, name, ispkg in pkgutil.walk_packages(comp_pkg.__path__):
            if not ispkg:
                continue

            full_pkg_path = '{}.{}'.format(comp_pkg_name, name)
            try:
                #
                # Look for the component module in the package
                #
                comp_inst_mod = importlib.import_module(
                    '{}.component'.format(full_pkg_path))

                #
                # Look for the ComponentInstaller class in the module
                #
                if not hasattr(comp_inst_mod, 'ComponentInstaller'):
                    logger.warning(
                        'ComponentInstaller class not found: %s',
                        full_pkg_path
                    )

                #
                # Initialize the ComponentInstaller class and register
                # it with the KitInstaller
                #
                comp_inst_class = comp_inst_mod.ComponentInstaller
                comp_inst = comp_inst_class(self)
                comp_inst.session = self.session
                self._component_installers[comp_inst_class.name] = \
                    comp_inst

                logger.debug(
                    'Component installer registered: %s', comp_inst.spec
                )

            except ModuleNotFoundError:
                logger.debug('Package not a component: %s', full_pkg_path)

            self._component_installers_loaded = True

    def is_installable(self):
        """
        Determines whether or not this kit is installable under the given
        conditions/circumstances. Override this in your implementations as
        necessary.

        :return: True if it is installable, False otherwise.

        """
        return True

    def run_action(self, action_name, *args, **kwargs):
        """
        Runs the specified action.

        :param action_name: the name of the action to run

        """
        try:
            action = getattr(self, 'action_{}'.format(action_name))

            return action(*args, **kwargs)
        except KeyError:
            raise Exception('Unknown action: {}'.format(action_name))

    def get_kit(self):
        """
        Gets the Kit instance for this kit.

        :return: a Kit instance

        """
        kit = Kit(
            name=self.name,
            version=self.version,
            iteration=self.iteration
        )
        kit.setDescription(self.meta.get('description', None))
        for component_installer in self.get_all_component_installers():
            kit.addComponent(component_installer.get_component())
        return kit

    def get_eula(self):
        """
        Gets the EULA for this kit, if it exists.

        :return: a Eula instance if there is a EULA file, otherwise None.

        """
        eula = None
        eula_path = os.path.join(self.install_path, EULA_FILE)
        if os.path.exists(eula_path) and os.path.isfile(eula_path):
            eula_fp = open(eula_path)
            text = eula_fp.read()
            eula_fp.close()
            eula = Eula(text=text)
        else:
            logger.debug('EULA not found: %s', eula_path)

        return eula

    def get_component_installer(self, component_name: str):
        self._load_component_installers()
        return self._component_installers.get(component_name)

    def get_all_component_installers(self):
        self._load_component_installers()
        return [ci for ci in self._component_installers.values()]

    def register_database_table_mappers(self):
        """
        Register database table mappers for this kit.

        """

        kit_pkg_name = inspect.getmodule(self).__package__

        db_table_pkg_name = '{}.db.models'.format(kit_pkg_name)

        logger.debug(
            'Searching for database table mappers in package: %s',
            db_table_pkg_name
        )

        try:
            importlib.import_module(db_table_pkg_name)
        except ModuleNotFoundError:
            logger.debug(
                'No database table mappers found for kit: %s', self.spec
            )

    def register_web_service_controllers(self):
        """
        Register web service controllers for this kit.

        """

        kit_pkg_name = inspect.getmodule(self).__package__

        ws_pkg_name = '{}.web_service.controllers'.format(kit_pkg_name)

        logger.debug(
            'Searching for web service controllers in package: %s',
            ws_pkg_name
        )

        try:
            importlib.import_module(ws_pkg_name)
        except ModuleNotFoundError:
            logger.debug(
                'No web service controllers found for kit: %s',
                self.spec
            )

    def register_event_listeners(self):
        """
        Register event listeners for this kit.

        """

        kit_pkg_name = inspect.getmodule(self).__package__

        listener_pkg_name = '{}.events.listeners'.format(kit_pkg_name)

        logger.debug(
            'Searching for event listeners in package: %s',
            listener_pkg_name
        )

        try:
            importlib.import_module(listener_pkg_name)
        except ModuleNotFoundError:
            logger.debug(
                'No event listeners found for kit: %s', self.spec)

    def action_install_puppet_modules(self, *args, **kwargs):
        #
        # Prevent circular import
        #
        from .actions import InstallPuppetModulesAction
        return InstallPuppetModulesAction(self)(*args, **kwargs)

    def action_pre_install(self):
        pass

    def action_pre_uninstall(self):
        pass

    def action_post_install(self):
        #
        # Check for python packages to install
        #
        pkg_dir = os.path.join(
            self.install_path,
            'python_packages'
        )
        if os.path.exists(pkg_dir):
            self._update_python_repo(pkg_dir)

        #
        # Install required python packages from requirements.txt
        #
        requirements_path = os.path.join(
            self.kit_path,
            'requirements.txt'
        )
        pip_install_requirements(requirements_path)

    def _update_python_repo(self, pkg_dir: str):
        """
        Updates the Tortuga Python repo with packages from the kit.

        :param pkg_dir: the source directory from which the packages will
                        be copied

        """
        #
        # Copy the files from the pkg_dir to the Tortuga repo
        #
        whl_path = os.path.join(pkg_dir, '*.whl')
        repo_path = os.path.join(
            self.config_manager.getTortugaIntWebRoot(),
            'python-tortuga'
        )

        cmd = 'rsync -a {} {}'.format(whl_path, repo_path)

        logger.debug(cmd)

        executeCommand(cmd)

        #
        # Re-build the package index
        #
        dir2pi = os.path.join(
            self.config_manager.getBinDir(),
            'dir2pi'
        )

        cmd = '{} {}'.format(dir2pi, repo_path)

        logger.debug(cmd)

        executeCommand(cmd)

    def action_post_uninstall(self):
        pass

    def action_uninstall_puppet_modules(self, *args, **kwargs):
        #
        # Prevent circular import
        #
        from .actions import UninstallPuppetModulesAction
        return UninstallPuppetModulesAction(self)(*args, **kwargs)

    def action_get_metadata(self,
                            hardware_profile_name: Optional[str] = None,
                            software_profile_name: Optional[str] = None,
                            node_name: Optional[str] = None) -> dict:
        pass


class ComponentInstallerBase(ConfigurableMixin):
    config_type = 'component'

    name = None
    version = None
    os_list = []

    #
    # Attributes, provided by instances of this class
    #
    installer_only = False
    compute_only = False

    def __init__(self, kit_installer):
        self.kit_installer = kit_installer
        self.spec = (self.kit_installer.spec, self.name, self.version)

        #
        # Setup paths
        #
        self.component_path = os.path.dirname(inspect.getfile(self.__class__))
        self.files_path = os.path.join(
            self.component_path,
            'files'
        )

        #
        # Initialize configuration
        #
        super().__init__()

    def get_config_base(self):
        return self.kit_installer.get_config_base()

    def is_enableable(self, software_profile):
        """
        Determines whether this component can be enabled under the
        given conditions/circumstances. Override this in your
        implementations as necessary.

        :param software_profile: the software profile to test

        :return:                 True if it can be enabled, False otherwise.

        """
        node_type = software_profile.getType()

        if node_type != 'installer' and self.installer_only:
            raise ConfigurationError(
                'Component can only be enabled on installer software'
                'profiles: {}'.format(self.name))

        if node_type == 'installer' and self.compute_only:
            raise ConfigurationError(
                'Component can only be enabled on compute software'
                'profiles: {}'.format(self.name))

        return True

    def run_action(self, action_name, *args, **kwargs):
        """
        Runs the specified action.

        :param action_name: the name of the action to run

        """
        try:
            action = getattr(self, 'action_{}'.format(action_name))

            return action(*args, **kwargs)
        except KeyError:
            raise Exception('Unknown action: {}'.format(action_name))

    def get_component(self):
        """
        Gets a Component instance for this component.

        :return: a Component instance

        """
        component = Component(
            name=self.name,
            version=self.version
        )
        for os_spec in self.os_list:
            component.addOsFamilyInfo(
                OsFamilyInfo(name=os_spec['family'],
                             version=os_spec['version'],
                             arch=os_spec['arch'])
            )
        return component

    @property
    def puppet_class(self) -> str:
        """
        Returns the puppet module for this component, typically as follows:

            puppet_module::component_name

        :return str: the puppet class name for this component

        """
        default_module = 'tortuga_kit_{}'.format(
            self.kit_installer.name.lower().replace('-', '_'))
        if self.kit_installer.puppet_modules:
            #
            # Puppet modules are defined as:
            #
            #     univa-module_name
            #
            # So we want to split off the prefix before the hyphen to get
            # the actual module name
            #
            default_module = \
                self.kit_installer.puppet_modules[0].split('-')[-1]
        return '{}::{}'.format(default_module, self.name.lower())

    def action_add_host(self, hardware_profile_name, software_profile_name,
                        nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when adding a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) added
        :param args:
        :param kwargs:

        """
        pass

    def action_configure(self, software_profile_name, *args, **kwargs):
        pass

    def action_delete_host(self, hardware_profile_name, software_profile_name,
                           nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass

    def action_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer when the component is enabled
        on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_get_cloud_config(self, node, hardware_profile,
                                software_profile, user_data, *args, **kwargs):
        pass

    def action_get_puppet_args(self, db_software_profile,
                               db_hardware_profile,
                               *args, **kwargs):
        return {}

    def action_pre_add_host(self, hardware_profile, software_profile,
                            hostname, ip, *args, **kwargs):
        """
        This hook is invoked on the installer prior to adding a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile of the host being added
        :param software_profile: the software profile of the host being added
        :param hostname:         the hostname of the host being added
        :param ip:               the ip address of the host being added
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_delete_host(self, hardware_profile, software_profile,
                               nodes, *args, **kwargs):
        """
        This hook is invoked on the installer piror to deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile
        :param software_profile: the software profile
        :param nodes:            the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to enabling the
        component on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_install(self, *args, **kwargs):
        pass

    def action_pre_remove(self, *args, **kwargs):
        pass

    def action_post_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component was disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_post_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after the component has been
        enabled on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_post_install(self, *args, **kwargs):
        pass

    def action_post_remove(self, *args, **kwargs):
        pass

    def action_refresh(self, software_profile_list, *args, **kwargs):
        pass
