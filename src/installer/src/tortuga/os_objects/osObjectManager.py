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
from typing import Optional

from tortuga.config.configManager import ConfigManager
from tortuga.logging import OS_NAMESPACE
from tortuga.os_utility import tortugaSubprocess


class OsObjectManager:
    """
    Base tortuga os object manager class.

    """
    def __init__(self, configManager: Optional[ConfigManager] = None) -> None:
        self._logger = logging.getLogger(OS_NAMESPACE)
        self._cm = configManager if configManager else ConfigManager()

    def execute(self, cmd, echo: bool = False): \
            # pylint: disable=unused-argument
        """
        Raises:
            TortugaException
        """

        return tortugaSubprocess.executeCommand(cmd)

    def executeAndIgnoreFailure(self, cmd):
        return tortugaSubprocess.executeCommandAndIgnoreFailure(cmd)
