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

import logging
import cherrypy
from cherrypy.lib import httpauth
from tortuga.utility import tortugaStatus
from tortuga.utility.authManager import AuthManager
from .tortugaController import TortugaController


SESSION_KEY = '_cp_username'


class TortugaHTTPAuthError(cherrypy.HTTPError):
    def set_response(self): \
            # pylint: disable=no-self-use
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        cherrypy.response.status = 401
        cherrypy.response.body = b'Authentication required'


def checkCredentials(username, password):
    """ Verifies credentials for username and password."""

    logger = logging.getLogger('tortuga.checkCredentials')
    logger.addHandler(logging.NullHandler())

    principal = AuthManager().getPrincipal(username, password)

    if principal is None:
        # See if there is a new admin available
        AuthManager().reloadPrincipals()

        principal = AuthManager().getPrincipal(
            username, password)

    if principal:
        logger.debug('Successful login from user [%s]' % (username))

        if 'id' in principal.getAttributes():
            cherrypy.session['admin_id'] = principal.getAttributes()['id']

        return None

    logger.warn('Web service login denied for user [%s]' % (username))

    sess = cherrypy.session

    badusername = sess.get(SESSION_KEY, None)

    sess[SESSION_KEY] = None

    if badusername:
        cherrypy.request.login = None

    return 'Incorrect username or password.'


def checkAuth(*args):   # pylint: disable=unused-argument
    """
    A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list
    of conditions that the user must fulfill.
    """

    logger = logging.getLogger('tortuga.checkAuth')
    logger.addHandler(logging.NullHandler())

    conditions = cherrypy.request.config.get('auth.require', None)

    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)

        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    # Send old page as fromPage parameter
                    logger.debug(
                        'Authorization failed for: %s ' % (username))

                    raise TortugaHTTPAuthError()
        else:
            username = None
            password = None

            if 'authorization' not in cherrypy.request.headers:
                raise TortugaHTTPAuthError()

            authorization = cherrypy.request.headers['authorization']

            ah = httpauth.parseAuthorization(authorization)

            if ah['auth_scheme'] == 'basic':
                username = ah['username']
                password = ah['password']

            if username and password and \
                    not checkCredentials(username, password):
                return

            raise TortugaHTTPAuthError()


cherrypy.tools.auth = cherrypy.Tool('before_handler', checkAuth)


def require(*conditions):
    """
    A decorator that appends conditions to the auth.require config
    variable.
    """

    # pylint: disable=W0212

    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f

    return decorate


# Conditions are callables that return True if the user
# fulfills the conditions they define, False otherwise.
# They can access the current username as cherrypy.request.login
def memberOf(groupname):
    def check():
        return cherrypy.request.login == 'cbrunner' and groupname == 'admin'

    return check


def nameIs(reqd_username):
    return lambda: reqd_username == cherrypy.request.login


def anyOf(*conditions):
    """ Returns True if any of the conditions match. """

    def check():
        for c in conditions:
            if c():
                return True

        return False

    return check


def allOf(*conditions):
    """ Returns True if all of the conditions match. """

    def check():
        for c in conditions:
            if not c():
                return False

        return True

    return check


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
    def login(self, username=None, password=None, fromPage='/'): \
            # pylint: disable=unused-argument
        if int(cherrypy.request.headers['Content-Length']):
            postdata = cherrypy.request.json
        else:
            postdata = {}

        username = postdata['username'] if 'username' in postdata else None
        password = postdata['password'] if 'password' in postdata else None

        if username is None or password is None:
            logger = logging.getLogger('tortuga.login')
            logger.addHandler(logging.NullHandler())

            logger.debug('Going for Basic Authentication')

            authorization = cherrypy.request.headers['Authorization']

            logger.debug('Authorization: %s' % (authorization))

            ah = httpauth.parseAuthorization(authorization)

            if ah['auth_scheme'] == 'basic':
                username = ah['username']
                password = ah['password']

        if username is None or password is None:
            logger.debug(
                'Either username and/or password unspecified')

            return ''

        errorMsg = checkCredentials(username, password)

        if errorMsg:
            self.addTortugaResponseHeaders(
                tortugaStatus.TORTUGA_USER_NOT_AUTHORIZED_ERROR, errorMsg)

            cherrypy.response.status = 401

            return ''

        cherrypy.session[SESSION_KEY] = cherrypy.request.login = username

        self.addTortugaResponseHeaders(tortugaStatus.TORTUGA_OK)
