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

from tortuga.auth.manager import AuthManager
from tortuga.auth.methods import MultiAuthentionMethod
from tortuga.auth.principal import AuthPrincipal
from tortuga.exceptions.authenticationFailed import AuthenticationFailed
from .exceptions import TortugaHTTPAuthError


class CherryPyAuthenticator(MultiAuthentionMethod):
    """
    An authenticator designed to be run as a CherryPy tool.

    """
    def __call__(self, *args, **kwargs):
        if cherrypy.request.config.get('auth.required', False):
            self.authenticate(**kwargs)

    def authenticate(self, skip_callbacks: bool = False, **kwargs) -> str:
        try:
            return super().authenticate(skip_callbacks=skip_callbacks,
                                        **kwargs)
        except AuthenticationFailed:
            raise TortugaHTTPAuthError()

    def on_authentication_succeeded(self, username: str):
        super().on_authentication_succeeded(username)

        principal: AuthPrincipal = AuthManager().get_principal(username)
        principal_attributes: dict = principal.get_attributes()

        cherrypy.request.login = username
        cherrypy.session['admin_id']: int = \
            principal_attributes.get('id', None)

    def on_authentication_failed(self):
        cherrypy.request.login: str = None
        cherrypy.session['admin_id']: int = None
