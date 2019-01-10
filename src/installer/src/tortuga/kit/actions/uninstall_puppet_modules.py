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

import logging

from tortuga.logging import KITS_NAMESPACE
from tortuga.os_utility import tortugaSubprocess
from .base import KitActionBase

logger = logging.getLogger(KITS_NAMESPACE)


class UninstallPuppetModulesAction(KitActionBase):
    def do_action(self, *args, **kwargs):
        for module_name in self.kit_installer.puppet_modules:
            self._uninstall_puppet_module(module_name)

    def _uninstall_puppet_module(self, module_name):
        """
        Uninstalls a puppet module from the kit puppet_modules directory.

        :param module_name: The name of the puppet module to uninstall.

        """
        cmd = ('/opt/puppetlabs/bin/puppet module uninstall'
               ' --color false --ignore-changes {}'.format(module_name))
        tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)
