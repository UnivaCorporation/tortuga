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

import base64
import logging
from typing import Tuple

import cherrypy

from tortuga.auth.methods import (AuthenticationMethod,
                                  JwtAuthenticationMethod,
                                  UsernamePasswordAuthenticationMethod)
from tortuga.exceptions.authenticationFailed import AuthenticationFailed
from tortuga.logging import AUTH_NAMESPACE

logger = logging.getLogger(AUTH_NAMESPACE)


class AuthorizationHeaderMixin: \
        # pylint: disable=too-few-public-methods
    @staticmethod
    def parse_authorization_header() -> Tuple[str, str]:
        """
        Parses an authorization header.

        :return (str, str): the (scheme, value) of the authorization header

        """
        if 'authorization' not in cherrypy.request.headers:
            raise AuthenticationFailed()

        header = cherrypy.request.headers['authorization']
        parts = header.split(' ', 1)

        if len(parts) != 2:
            raise AuthenticationFailed()

        return parts[0], parts[1]


class HttpSessionAuthenticationMethod(AuthenticationMethod):
    """
    Authenticates a user based on a stored session key who's value is
    the username of the user.

    """
    SESSION_KEY = '_cp_username'

    def do_authentication(self, **kwargs) -> str:
        username: str = cherrypy.session.get(self.SESSION_KEY, None)
        if not username:
            raise AuthenticationFailed()
        return username

    def on_authentication_succeeded(self, username: str):
        cherrypy.session[self.SESSION_KEY] = username

    def on_authentication_failed(self):
        cherrypy.session[self.SESSION_KEY] = None


class HttpBasicAuthenticationMethod(AuthorizationHeaderMixin,
                                    UsernamePasswordAuthenticationMethod):
    """
    Authenticate a user via username password, via HTTP basic authentication.

    """
    def do_authentication(self, **kwargs) -> str:
        scheme, value = self.parse_authorization_header()
        if scheme.lower() != 'basic':
            raise AuthenticationFailed()

        username, password = self.parse_username_password(value)

        return super().do_authentication(username=username, password=password)

    def parse_username_password(self, encoded: str) -> Tuple[str, str]: \
            # pylint: disable=no-self-use
        """
        Parses an base64 encoded header value and extracts the username
        and password.

        :param encoded: the encoded string

        :return (str, str): the username and password

        """
        decoded: str = base64.b64decode(encoded).decode()
        parts = decoded.split(':')

        if len(parts) != 2:
            raise AuthenticationFailed()

        return parts[0], parts[1]


class HttpPostAuthenticatonMethod(UsernamePasswordAuthenticationMethod):
    """
    Authenticate a user via HTTP post data.

    """
    def do_authentication(self, **kwargs) -> str:
        if int(cherrypy.request.headers['Content-Length']):
            postdata = cherrypy.request.json
        else:
            postdata = {}

        username = postdata.get('username', None)
        password = postdata.get('password', None)

        return super().do_authentication(username=username,
                                         password=password, **kwargs)


class HttpJwtAuthenticationMethod(AuthorizationHeaderMixin,
                                  JwtAuthenticationMethod):
    """
    Authenticate a user via a HTTP JWT.

    """
    def do_authentication(self, **kwargs) -> str:
        scheme, value = self.parse_authorization_header()
        if scheme.lower() != 'bearer':
            raise AuthenticationFailed()

        return super().do_authentication(token=value)


class WsUsernamePasswordAuthenticationMethod(
        UsernamePasswordAuthenticationMethod):
    """
    Authenticate a websocket user using a username/password.

    """
    def do_authentication(self, **kwargs):
        #
        # An instance of tortuga.web_service.websocket.actions.BaseAction
        #
        action = kwargs.get('action', None)
        if not action:
            raise AuthenticationFailed()

        if action.method != 'password':
            raise AuthenticationFailed()

        username: str = action.data.get('username', None)
        password: str = action.data.get('password', None)
        if not username or not password:
            raise AuthenticationFailed()

        return super().do_authentication(username=username,
                                         password=password, **kwargs)


class WsJwtAuthenticationMethod(JwtAuthenticationMethod):
    """
    Authenticate a websocket user using via a JWT.

    """
    def do_authentication(self, **kwargs):
        #
        # An instance of tortuga.web_service.websocket.actions.BaseAction
        #
        action = kwargs.get('action', None)
        if not action:
            raise AuthenticationFailed()

        if action.method != 'jwt':
            raise AuthenticationFailed()

        token: str = action.data.get('token', None)
        if not token:
            raise AuthenticationFailed()

        return super().do_authentication(token=token, **kwargs)
