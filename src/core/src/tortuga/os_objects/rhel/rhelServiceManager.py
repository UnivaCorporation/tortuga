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

# pylint: disable=no-member

import os
import platform
import shutil

from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.os_objects.osObjectManager import OsObjectManager


class RhelServiceManager(OsObjectManager):
    """
    RHEL service manager.
    """

    SERVICE_SCRIPT_DIR = '/etc/init.d'

    SYSTEMCTL_PATH = '/usr/bin/systemctl'

    def __init__(self):
        OsObjectManager.__init__(self)

        # Use distribution version to determine whether or not to use systemd
        # instead of sysvinit scripts to manage services.
        self._use_systemctl = int(platform.dist()[1].split('.', 1)[0]) >= 7

    def start(self, serviceName, echo=False, clearState=True): \
            # pylint: disable=unused-argument
        """
        Start service.

            Returns:
                None
            Throws:
                CommandFailed
        """

        self.scheduleStartOnBoot(serviceName)

        cmd = '%s start %s' % (self.SYSTEMCTL_PATH, serviceName) \
            if self._use_systemctl else '/etc/init.d/%s start' % (serviceName)

        self.execute(cmd, echo)

    def restart(self, serviceName, echo=False):
        """
        Restart service.

            Returns:
                None
            Throws:
                CommandFailed
        """

        self.scheduleStartOnBoot(serviceName)

        cmd = '%s restart %s' % (self.SYSTEMCTL_PATH, serviceName) \
            if self._use_systemctl else \
            '/etc/init.d/%s restart' % (serviceName)

        self.execute(cmd, echo)

    def stop(self, serviceName, echo=False):
        """
        Stop service.

            Returns:
                None
            Throws:
                CommandFailed
        """

        cmd = '%s stop %s' % (self.SYSTEMCTL_PATH, serviceName) \
            if self._use_systemctl else '/etc/init.d/%s stop' % (serviceName)

        self.execute(cmd, echo)

    def scheduleStartOnBoot(self, serviceName):
        """
        Schedule service start on boot.

            Returns:
                None
            Throws:
                CommandFailed
        """

        cmd = '%s enable %s' % (self.SYSTEMCTL_PATH, serviceName) \
            if self._use_systemctl else '/sbin/chkconfig %s on' % (serviceName)

        self.execute(cmd)

    def unscheduleStartOnBoot(self, serviceName):
        """
        Do not schedule service start on boot.

            Returns:
                None
            Throws:
                CommandFailed
        """

        cmd = '%s disable %s' % (self.SYSTEMCTL_PATH, serviceName) \
            if self._use_systemctl else \
            '/sbin/chkconfig %s off' % (serviceName)

        self.execute(cmd)

    def installControlScript(self, scriptPath): \
            # pylint: disable=no-self-use
        """
        Install service control script.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """

        try:
            shutil.copy(scriptPath, RhelServiceManager.SERVICE_SCRIPT_DIR)
        except Exception as ex:
            raise CommandFailed(exception=ex)

    def uninstallControlScript(self, scriptName): \
            # pylint: disable=no-self-use
        """
        Uninstall service control script.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """

        try:
            os.remove(os.path.join(
                RhelServiceManager.SERVICE_SCRIPT_DIR,
                os.path.basename(scriptName)))
        except Exception as ex:
            raise CommandFailed(exception=ex)
