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

import json
import os
from logging import getLogger
from typing import List

from passlib.hash import pbkdf2_sha256

from tortuga.logging import AUTH_NAMESPACE
from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.jwt import JWT
from tortuga.admin.api import AdminApi
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.authenticationFailed import AuthenticationFailed

from .manager import AuthManager
from tortuga.web_service.database import dbm


logger = getLogger(AUTH_NAMESPACE)


class AuthenticationMethod:
    """
    Base authentication method class.

    """
    def authenticate(self, skip_callbacks: bool = False, **kwargs) -> str:
        """
        Performs the authentication, and returns the username.

        :param bool skip_callbacks: do not call the
                                    on_authentication_succeeded and
                                    on_authentication_failed callbacks

        :return: the username of the authenticated user.
        :raises AuthenticationFailed:

        """
        try:
            username: str = self.do_authentication(**kwargs)
            logger.debug(
                'Authentication succeeded: {} -> {}'.format(
                    username,
                    self.__class__
                )
            )
            if not skip_callbacks:
                self.on_authentication_succeeded(username)
            return username

        except AuthenticationFailed:
            logger.debug('Authentication failed: {}'.format(self.__class__))
            if not skip_callbacks:
                self.on_authentication_failed()
            raise

    def do_authentication(self, **kwargs) -> str:
        """
        Does the actual authentication, imeplement the actual mechanics of
        your method here.

        :return: the username of the authenticated user.
        :raises AuthenticationFailed:

        """
        pass

    def on_authentication_succeeded(self, username: str):
        """
        A callback that is called when a successful authentication has
        occurred, either via this authenticator, or any other one in the
        chain.

        :param username: the username of the successfully authenticated user

        """
        pass

    def on_authentication_failed(self):
        """
        A callback that is called when all authentication methods in the
        chain have failed.

        """
        pass


class MultiAuthentionMethod(AuthenticationMethod):
    """
    The Authentication method that supports attempting to authenticate
    against a number of other authentication methods, in order until it
    finds one that succeeds.

    """
    def __init__(self, methods: List[AuthenticationMethod] = None):
        """
        Initializer.

        :param methods List[AuthenticationMethod]: the list of authentication
                                                   methods to use

        """
        if not methods:
            methods = []
        self._methods: List[AuthenticationMethod] = methods

    def do_authentication(self, **kwargs) -> str:
        """
        Authenticates trying all authentication methods in order, and stopping
        after the first one succeeds.

        """
        username = None
        for method in self._methods:
            try:
                #
                # Skip the callbacks so that we can defer calling them
                # until we know for sure the final result of the
                # authentication chain
                #
                username = method.authenticate(skip_callbacks=True, **kwargs)
                if username:
                    break
            except AuthenticationFailed:
                pass

        if username:
            self.on_authentication_succeeded(username)
            return username
        else:
            self.on_authentication_failed()
            raise AuthenticationFailed()

    def on_authentication_succeeded(self, username: str):
        """
        A callback that is called every time a user has successfully
        authenticated.

        :param username: the username of the successfully authenticated user

        """
        for method in self._methods:
            method.on_authentication_succeeded(username)

    def on_authentication_failed(self):
        """
        A callback that is called every time a all authentication methods
        fail.

        """
        for method in self._methods:
            method.on_authentication_failed()


class UsernamePasswordAuthenticationMethod(AuthenticationMethod):
    """
    An authentication method that uses a username/password passed in as
    keyword arguments.

    """
    def do_authentication(self, **kwargs) -> str:
        """
        An authentication implementation that requires a username and
        password.

        :return str: the username
        :raises AuthenticationFailed:

        """
        username: str = kwargs.get('username', None)
        password: str = kwargs.get('password', None)

        if not username or not password:
            raise AuthenticationFailed()

        with dbm.session() as session:
            auth_manager = AuthManager(session=session)

            principal = auth_manager.get_principal(username)

            if not principal:
                #
                # See if there is a new admin available
                #
                auth_manager.reloadPrincipals()
                principal = auth_manager.get_principal(username)

            if not principal:
                raise AuthenticationFailed()

            if pbkdf2_sha256.verify(password, principal.get_password()):
                return username

            raise AuthenticationFailed()


class JwtAuthenticationMethod(AuthenticationMethod):
    """
    Authenticate a user via JWT tokens.

    """
    #
    # The path to the OpenID Connect Client configuration. See docs below
    # for the format of this file.
    #
    OPENID_CONNECT_CONFIG = 'openid_connect_client.json'

    def __init__(self, openid_connect_client: Client = None):
        self._client: Client = openid_connect_client
        if not openid_connect_client:
            self._configure_client()

    def do_authentication(self, **kwargs) -> str:
        if not self._client:
            logger.debug('No OpenID Connect Client configured')
            raise AuthenticationFailed()

        token: str = kwargs.get('token', None)
        if not token:
            logger.debug('No JWT token provided')
            raise AuthenticationFailed()

        try:
            jwt = JWT(keyjar=self._client.keyjar).unpack(token)
            self._client.verify_id_token(jwt, authn_req={})
            username = jwt['name']

        except Exception as ex:
            logger.info(str(ex))
            raise AuthenticationFailed()

        #
        # Assuming the token is valid, if we can't find the user, we
        # add them as an admin
        #
        with dbm.session() as session:
            if not AuthManager(session=session).get_principal(username):
                self._create_admin(session, username)

            return username

    def _create_admin(self, session, username):
        admin_api = AdminApi()
        admin_api.addAdmin(session, name=username)

    @staticmethod
    def openid_client_config_path():
        """
        The path to the OpenID Connect Client configuration. This is a JSON
        file with the following three settings:

        {
            "issuer": "http://example.com:123456/dex",
            "client_id": "client-id-1234",
            "client_secret": "AbcDef134..."
        }

        If this file does not exist, JWT authentication will be disabled.

        """
        cm = ConfigManager()

        return os.path.join(
            cm.getRoot(),
            'etc',
            JwtAuthenticationMethod.OPENID_CONNECT_CONFIG
        )

    def _configure_client(self):
        config_file_path = JwtAuthenticationMethod.openid_client_config_path()

        if not os.path.exists(config_file_path):
            logger.info(
                'OpenID Connect configuration ({}) not found, JWT'
                ' authentication is disabled'.format(config_file_path)
            )

            return

        with open(config_file_path) as fp:
            config = json.loads(fp.read())

            self._client = Client(
                client_authn_method=CLIENT_AUTHN_METHOD,
                verify_ssl='/etc/pki/tls/certs/ca-bundle.crt'
            )

            self._client.provider_config(config['issuer'])

            client_registration = RegistrationResponse(
                client_id=config['client_id'],
                client_secret=config['client_secret']
            )

            self._client.store_registration_info(client_registration)
