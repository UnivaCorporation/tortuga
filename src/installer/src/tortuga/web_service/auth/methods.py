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

import cherrypy
from cherrypy.lib import httpauth

from tortuga.auth.methods import AuthenticationMethod, \
    JwtAuthenticationMethod, UsernamePasswordAuthenticationMethod
from tortuga.exceptions.authenticationFailed import AuthenticationFailed


logger = getLogger(__name__)


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


class HttpBasicAuthenticationMethod(UsernamePasswordAuthenticationMethod):
    """
    Authenticate a user via username password, via HTTP basic authentication.

    """
    SCHEME = 'basic'

    def do_authentication(self, **kwargs) -> str:
        username = None
        password = None

        if 'authorization' in cherrypy.request.headers:
            authorization = cherrypy.request.headers['authorization']
            ah = httpauth.parseAuthorization(authorization)
            if ah['auth_scheme'] == 'basic':
                username = ah['username']
                password = ah['password']

        return super().do_authentication(username=username, password=password)


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


class HttpJwtAuthenticationMethod(JwtAuthenticationMethod):
    """
    Authenticate a user via a HTTP JWT.

    """
    def do_authentication(self, **kwargs) -> str:
        if 'authorization' not in cherrypy.request.headers:
            raise AuthenticationFailed()

        authorization = cherrypy.request.headers['authorization']
        scheme, value = self._parse_authorization_header(authorization)
        if not value or not scheme or scheme.lower() != 'bearer':
            raise AuthenticationFailed()

        return super().do_authentication(token=value)

    @staticmethod
    def _parse_authorization_header(header: str) -> (str, str):
        """
        Parses an authentication header.

        :param str header: the header string to parse

        :return (str, str): the (scheme, value) of the authorization header

        """
        scheme = None
        value = None

        parts = header.split(' ', 1)
        if parts:
            scheme = parts[0]
        if len(parts) > 1:
            value = parts[1]

        return scheme, value


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
