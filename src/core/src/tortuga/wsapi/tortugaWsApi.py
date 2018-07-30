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

from logging import getLogger
from typing import Optional

from tortuga.config.configManager import ConfigManager
from .client import RestApiClient


logger = getLogger(__name__)


WS_API_VERSION = 'v1'


class TortugaWsApi(RestApiClient):
    """
    Base tortuga ws api class.
    """

    def __init__(self, username: Optional[str] = None,
                 password: Optional[str] = None,
                 baseurl: Optional[str] = None,
                 verify: bool = True):

        self._cm = ConfigManager()

        if not baseurl:
            baseurl = '{}://{}:{}'.format(
                self._cm.getAdminScheme(),
                self._cm.getInstaller(),
                self._cm.getAdminPort()
            )

        if username is None and password is None:
            logger.debug('Using built-in user credentials')
            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()

        super().__init__(username, password, baseurl, verify)

        self.baseurl = '{}/{}'.format(self.baseurl, WS_API_VERSION)
