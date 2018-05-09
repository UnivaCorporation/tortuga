from logging import getLogger

from .base import KitActionBase
from tortuga.os_utility import tortugaSubprocess


logger = getLogger(__name__)


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
