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

import cherrypy

from tortuga.utility import tortugaStatus
from .tortugaController import TortugaController
from .. import auth


class AuthController(TortugaController):
    """
    Controller to provide login and logout actions.

    """
    actions = [
        {
            'name': 'auth',
            'path': '/v1/auth/login',
            'action': 'login',
            'method': ['GET', 'PUT', 'POST', 'DELETE']
        }
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def login(self):
        #
        # Setup a list of authentication methods that we are willing to
        # accept here, in the order that we would like them to be tried
        #
        authentication_methods = [
            auth.HttpPostAuthenticatonMethod(),
            auth.HttpBasicAuthenticationMethod(),
            auth.HttpSessionAuthenticationMethod(),
            auth.HttpJwtAuthenticationMethod()
        ]
        authenticator = auth.CherryPyAuthenticator(authentication_methods)

        try:
            authenticator.authenticate()
            self.addTortugaResponseHeaders(tortugaStatus.TORTUGA_OK)

        except auth.TortugaHTTPAuthError:
            self.addTortugaResponseHeaders(
                tortugaStatus.TORTUGA_USER_NOT_AUTHORIZED_ERROR,
                'Authentication failed'
            )
            cherrypy.response.status = 401
