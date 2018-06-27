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

import glob
import os
from logging import getLogger

from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.os_utility import tortugaSubprocess

from .base import KitActionBase

logger = getLogger(__name__)


class InstallPuppetModulesAction(KitActionBase):
    def do_action(self, *args, **kwargs):
        for module_name in self.kit_installer.puppet_modules:
            self._install_puppet_module(module_name)

    def _install_puppet_module(self, module_name):
        """
        Installs a puppet module from the kit puppet_modules directory.

        :param module_name: The name of the puppet module to install.

        """
        files = glob.glob(
            os.path.join(
                self.kit_installer.puppet_modules_path,
                '{}-*.tar.gz'.format(module_name)
            )
        )
        if not files:
            errmsg = f'Unable to find Puppet module {module_name}'

            logger.error(errmsg)

            raise ConfigurationError(errmsg)

        logger.info('Installing Puppet module {}'.format(module_name))

        cmd = ('/opt/puppetlabs/bin/puppet module install --color false'
               ' {}'.format(files[0]))

        tortugaSubprocess.executeCommand(cmd)
