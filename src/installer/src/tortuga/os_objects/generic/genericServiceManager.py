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

import os
import inspect
from subprocess import Popen, PIPE


class Systemctl(object):
    """
    Provide primitives for systemctl.
    """
    def __init__(self, service):
        """
        Initialise with service name.

        :param service: String service name
        :returns: Systemctl object
        """
        self.service = service

    def _make_exec_list(self, command):
        """
        Make an execution list for Popen.

        :param command: String command
        :returns: List execution
        """
        execute = ['systemctl']
        execute.append(command)
        execute.append(self.service)

        return execute

    def _exec_systemctl(self, override=None):
        """
        Execute systemctl command.

        :param override: String override command
        :return: Process object
        """
        if override:
            command = override
        else:
            # Get calling method's name
            command = inspect.stack()[1][3]

        process = Popen(
            self._make_exec_list(command),
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )

        process.communicate()
        process.wait()

        return process

    def exists(self):
        """
        Check if service exists.

        :returns: Boolean
        """
        return os.path.isfile(
            '/usr/lib/systemd/system/{}.service'.format(
                self.service
            )
        )

    def is_active(self):
        """
        Get the service's status.

        :returns: Boolean is active
        """
        process = self._exec_systemctl('is-active')

        if process.returncode == 0:
            return True
        return False

    def enable(self):
        """
        Enable the service.

        :returns: None
        """
        self._exec_systemctl()

    def disable(self):
        """
        Disable the service.

        :returns: None
        """
        self._exec_systemctl()

    def start(self, enable=True):
        """
        Start the service.

        :param enable: Boolean also enable the service
        :returns: None
        """
        self._exec_systemctl()
        if enable:
            self.enable()

    def stop(self, disable=True):
        """
        Stop the service.

        :param disable: Boolean also disable the service
        :returns: None
        """
        self._exec_systemctl()
        if disable:
            self.disable()

    def restart(self):
        """
        Restart the service.

        :returns: None
        """
        self._exec_systemctl()
