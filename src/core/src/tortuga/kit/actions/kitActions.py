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

# pylint: disable=no-self-use,no-member

'''
Kit and Component classes

The classes provide the basis for the Kit Integration Modules described in
"Abstract Kit Representation."

A kit is a group of components that constitutes a complete application. A
component is an indivisible "feature" of an application; e.g., a telnet
kit might contain a client component and a server component.

The purpose of abstracting the kit is to represent, bundle, distribute,
and install a complete application into a Tortuga software repository,
along with any information about any external kits and/or packages the
kit may depend upon in a run-time environment. (A Tortuga software
repository resides on a Installer Node.) The purpose is not to
install the software onto a machine so that it may be run there; the
purpose is to provide the underlying operating system's native package
manager with the necessary files and meta-data so it can install the
software.
'''

import os
import glob
import subprocess
import json

from tortuga.config.configManager import ConfigManager
from tortuga.kit.actions.actionsBase import ActionsBase
from tortuga.exceptions.componentNotFound import ComponentNotFound
from tortuga.os_utility import tortugaSubprocess
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.fileNotFound import FileNotFound


class KitActions(ActionsBase):
    '''
    A kit is a group of components that constitute a complete application.
    '''

    def __init__(self, moduledir=None):
        '''
        Arguments:

            moduledir   Path to the module's directory. Defaults to CWD.
                        E.g: "/opt/tortuga/kits/kit-ganglia-1.2.3"

        Attributes:

            name        Kit name.

            version     Kit version.

            moduledir   Fully-qualified path to the root of the kit as
                        installed on the filesystem. For example,
                        "/opt/tortuga/kits/kit-ganglia-1.2.3"

            components  a list of ComponentActions() objects

            _logger	A logger instance for creating log messages
            _config     configManager instance
            _root       $TORTUGA_ROOT; e.g: "/opt/tortuga"
        '''

        super(KitActions, self).__init__()

        self.name = self.__class__.__name__.lower()
        self.version = None

        if moduledir:
            self.moduledir = moduledir
        else:
            self.moduledir = os.getcwd()

        self.components = []

        # Most kits need these things; including here for convenience.

        self._config = ConfigManager()
        self._root = self._config.getRoot()

    @property
    def config(self):
        return self._config

    def getLogger(self):
        return self._logger

    def getConfigManager(self):
        return self._config

    def getRoot(self):
        return self._root

    # Overridden form ActionsBase
    def getConfigFile(self):
        return "%s/%s-kit.conf" % (self.getConfigBase(), self.name.lower())

    def getConfigBase(self):
        return "%s/%s" % (
            self.getConfigManager().getKitConfigBase(), self.name.lower())

    def pre_install(self):
        ''' Pre-installation kit hook. '''
        pass

    def post_install(self):
        ''' Post-installation kit hook. '''
        pass

    def pre_uninstall(self):
        ''' Post-uninstallation kit hook. '''
        pass

    def post_uninstall(self):
        ''' Post-uninstallation kit hook. '''
        pass

    def add_component(self, component):
        '''Add the given component to the kit's list of components'''

        # Point the component to its parent
        component.kit = self
        self.components.append(component)

    def lookup_cname(self, cname):
        '''
        Return the ComponentActions object from the KitActions whose
        name is "cname"

        Raises:
            ComponentNotFound
        '''
        for c in self.components:
            if c.__component_name__ == cname:
                return c(self)

        raise ComponentNotFound(
            "Can't find component [%s] in kit [%s]" % (
                cname, self.__class__.__name__))

    def is_puppet_module_installed(self, name):
        cmd = '/opt/puppetlabs/bin/puppet module list --render-as=json'

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        puppet_module_list = json.load(p.stdout)

        retval = p.wait()

        if retval != 0:
            return None

        for modules in \
                puppet_module_list['modules_by_path'].values():
            for module in modules:
                if module.startswith('Module %s(' % (name)):
                    return True

        return False

    def installPuppetModule(self, modulePath):
        """
        Install "standard" Puppet module using "puppet module install --force"

        Raises:
            ConfigurationError
        """

        if not os.path.exists(modulePath):
            errmsg = ('Error: unable to install puppet module [%s].'
                      ' Module does not exist' % (modulePath))

            self.getLogger().error(errmsg)

            raise ConfigurationError(errmsg)

        cmd = ('/opt/puppetlabs/bin/puppet module install --color false'
               ' --force %s' % (modulePath))

        tortugaSubprocess.executeCommand(cmd)

    def uninstallPuppetModule(self, moduleName):
        cmd = ('/opt/puppetlabs/bin/puppet module uninstall'
               ' --color false --ignore-changes %s' % (moduleName))
        tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def install_wheel_matching_filespec(self, whl_pathspec):
        # Find an whl matching the filespec
        whl_files = glob.glob(whl_pathspec)

        if not whl_files:
            raise FileNotFound(
                'No files found matching spec %s' % (whl_pathspec))

        # Use the first whl file found
        cmd = '%s/pip install %s' % (
            self._config.getBinDir(), whl_files[0])

        tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def uninstall_wheel(self, wheel_name):
        cmd = 'pip uninstall %s' % (wheel_name)

        tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)
