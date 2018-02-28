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

from tortuga.exceptions.abstractMethod import AbstractMethod


class OsServiceManagerInterface(object):
    """
    OS service manager interface.
    """

    def start(self, serviceName, echo=False, clearState=True): \
            # pylint: disable=no-self-use,unused-argument
        """
        Start service.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('startService() has to be implemented in the'
                             ' concrete API class.')

    def restart(self, serviceName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Restart service.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('restartService() has to be implemented in'
                             ' the concrete API class.')

    def stop(self, serviceName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Stop service.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('stopService() has to be implemented in the'
                             ' concrete API class.')

    def scheduleStartOnBoot(self, serviceName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Schedule service start on boot.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('scheduleStartOnBoot() has to be implemented'
                             ' in the concrete API class.')

    def unscheduleStartOnBoot(self, serviceName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Do not schedule service start on boot.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('unscheduleStartOnBoot() has to be'
                             ' implemented in the concrete API class.')

    def installControlScript(self, scriptPath): \
            # pylint: disable=no-self-use,unused-argument
        """
        Install service control script.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('installControlScript() has to be implemented'
                             ' in the concrete API class.')

    def uninstallControlScript(self, scriptName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Uninstall service control script.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """
        raise AbstractMethod('uninstallControlScript() has to be'
                             ' implemented in the concrete API class.')
