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
from typing import Optional

from tortuga.config.configManager import ConfigManager
from tortuga.wsapi.client import RestApiClient


logger = logging.getLogger(__name__)


WS_API_VERSION = 'v2'


class TortugaWsApiClient:
    """
    Tortuga ws api client class.

    """
    def __init__(self, endpoint: str,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 base_url: Optional[str] = None,
                 verify: bool = True) -> None:

        self._cm = ConfigManager()

        if not base_url:
            base_url = '{}://{}:{}'.format(
                self._cm.getAdminScheme(),
                self._cm.getInstaller(),
                self._cm.getAdminPort()
            )

        if username is None and password is None:
            logger.debug('Using built-in user credentials')
            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()

        self._client = RestApiClient(
            username=username,
            password=password,
            baseurl=base_url,
            verify=verify
        )

        self._client.baseurl = '{}/{}/{}/'.format(base_url, WS_API_VERSION,
                                                  endpoint)

    def _build_query_string(self, params: dict) -> str: \
            # pylint: disable=no-self-use
        return '&'.join([f'{k}={v}' for k, v in params.items()])

    def list(self, **params) -> list:
        path = '/'
        query_string = self._build_query_string(params)
        if query_string:
            path += '?{}'.format(query_string)

        return self._client.get(path)

    def get(self, id_: str) -> dict:
        path = '/{}'.format(id_)

        return self._client.get(path)
