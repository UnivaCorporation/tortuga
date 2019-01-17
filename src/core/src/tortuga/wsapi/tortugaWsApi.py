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

import requests

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.logging import WEBSERVICE_CLIENT_NAMESPACE
from tortuga.utility import tortugaStatus
from .client import RestApiClient


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
        self._logger = logging.getLogger(WEBSERVICE_CLIENT_NAMESPACE)

        if not baseurl:
            baseurl = '{}://{}:{}'.format(
                self._cm.getAdminScheme(),
                self._cm.getInstaller(),
                self._cm.getAdminPort()
            )

        if username is None and password is None:
            self._logger.debug('Using built-in user credentials')
            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()

        super().__init__(username, password, baseurl, verify)

        self.baseurl = '{}/{}'.format(self.baseurl, WS_API_VERSION)

    def process_response(self, response: requests.Response):
        check_status(response.headers)

        return super().process_response(response)


def check_status(http_headers: dict):
    """
    Map tortuga status code into appropriate exception.

    :param http_headers:

    """
    code = http_headers.get('Tortuga-Status-Code', None)
    msg = http_headers.get('Tortuga-Status-Message', 'Internal Error')

    if code is None or code == str(tortugaStatus.TORTUGA_OK):
        return

    if int(code) in tortugaStatus.exceptionMap:
        #
        # Exception string is value of the form 'x.y.z'
        # where 'x.y' is tortuga module, and 'z' class in that module
        #
        ex_str = tortugaStatus.exceptionMap.get(int(code))
        ex_class = ex_str.split('.')[-1]              # 'z' in 'x.y.z'
        ex_module = '.'.join(ex_str.split('.')[:-1])  # 'x.y' in 'x.y.z'

        module_ = __import__(
            'tortuga.{0}'.format(ex_module), globals(), locals(),
            [ex_class], 0)

        Exception_ = getattr(module_, ex_class)

        raise Exception_(msg)

    raise TortugaException(msg)
