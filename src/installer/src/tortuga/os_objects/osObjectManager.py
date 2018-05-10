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

# pylint: disable=no-self-use

import logging
from tortuga.os_utility import tortugaSubprocess
from tortuga.config.configManager import ConfigManager


class OsObjectManager(object):
    """
    Base tortuga os object manager class.
    """
    def __init__(self):
        self._logger = logging.\
            getLogger('tortuga.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())
        self._cm = ConfigManager()

    def execute(self, cmd, echo=False):
        """
        Raises:
            TortugaException
        """

        if echo:
            return tortugaSubprocess.executeCommandAndLogToStdOut(cmd)
        else:
            return tortugaSubprocess.executeCommand(cmd)

    def executeAndIgnoreFailure(self, cmd):
        return tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)

    def getLogger(self):
        """ Get logger for this class. """
        return self._logger
