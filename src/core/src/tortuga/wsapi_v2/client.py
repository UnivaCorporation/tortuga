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
from typing import Optional, Union

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.userNotAuthorized import UserNotAuthorized
from tortuga.web_client import sessionManager


logger = logging.getLogger(__name__)


class TortugaWsApiClient:
    """
    Tortuga ws api client class.

    """
    API_VERSION = 'v2'

    def __init__(self, endpoint: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 base_url: Optional[str] = None,
                 verify: bool = True) -> None:
        logger.addHandler(logging.NullHandler())

        #
        # Validate that we have either a base URL or and endpoint, but
        # not both
        #
        if not endpoint and not base_url:
            raise Exception(
                'Either a base_url or an endpoint must be provided')
        if endpoint and base_url:
            raise Exception(
                'Either a base_url or an endpoint must be provided, not both')

        self._cm = ConfigManager()
        self._sm: Union[sessionManager.SessionManager, None] = None

        #
        # Initialize the base URL
        #
        if base_url:
            self._svr_base_url = base_url
        else:
            self._svr_hostname = self._cm.getInstaller()
            self._svr_port = self._cm.getAdminPort()
            self._svr_scheme = self._cm.getAdminScheme()
            self._svr_base_url = '{}://{}:{}'.format(
                self._svr_scheme,
                self._svr_hostname,
                self._svr_port
            )

        self._svr_endpoint_url = '{}/{}/{}/'.format(self._svr_base_url,
                                                    self.API_VERSION,
                                                    endpoint)
        #
        # Initialize the username and password
        #
        if username is None and password is None:
            logger.debug('Using built-in user credentials')
            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()
        self._username = username
        self._password = password

        self._verify = verify

    def _get_session_manager(self):
        if not self._sm:
            self._sm = sessionManager.createSession()
        return self._sm

    def send_session_request(self, url: str, method: str = 'GET',
                             content_type: str = 'application/json',
                             accept_type='application/json',
                             data=None) -> str:
        sm = self._get_session_manager()
        if not sm.hasSession():
            if self._username is None:
                raise UserNotAuthorized('Username not supplied')
            if self._password is None:
                raise UserNotAuthorized('Password not supplied')
            #
            # establishSession() sets the 'wsUrl' so the explicit call
            # to setHost() is not required
            #
            sm.establishSession(self._svr_base_url, self._username,
                                self._password)
        return sm.sendRequest(url, method, content_type, data, accept_type,
                              verify=self._verify)

    def send_request(self, url: str, method: str = 'GET',
                     content_type: str = 'application/json',
                     accept_type: str = 'application/json',
                     data: dict = None) -> str:
        sm = self._get_session_manager()
        #
        # Because there's no call to establishSession(), explicitly call
        # setHost()
        #
        sm.setHost(url)
        return sm.sendRequest(url, method, content_type, data, accept_type,
                              verify=self._verify)

    def list(self, **params) -> str:
        url = self._svr_endpoint_url
        query_string = self._build_query_string(params)
        if query_string:
            url += '?{}'.format(query_string)
        _, response = self.send_session_request(url)

        return response

    def _build_query_string(self, params: dict) \
            -> str:  # pylint: disable=no-self-use
        return '&'.join([f'{k}={v}' for k, v in params.items()])

    def get(self, id_: str) -> str:
        #
        # Build URL
        #
        url = '{}/{}'.format(self._svr_endpoint_url, id_)
        _, response = self.send_session_request(url)

        return response
