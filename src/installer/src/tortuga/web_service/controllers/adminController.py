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

import cherrypy

from tortuga.admin.api import AdminApi
from tortuga.auth.methods import UsernamePasswordAuthenticationMethod
from tortuga.objects.admin import Admin
from tortuga.utility.helper import str2bool
from tortuga.web_service.auth.decorators import authentication_required
from .tortugaController import TortugaController


class AdminController(TortugaController):
    """
    Update controller class.

    """
    actions = [
        {
            'name': 'addAdmin',
            'path': '/v1/admins/',
            'action': 'addAdmin',
            'method': ['POST'],
        },
        {
            'name': 'getAdminList',
            'path': '/v1/admins/',
            'action': 'getAdminList',
            'method': ['GET'],
        },
        {
            'name': 'getAdmin',
            'path': '/v1/admins/:(admin_id)',
            'action': 'getAdmin',
            'method': ['GET'],
        },
        {
            'name': 'adminUpdate',
            'path': '/v1/admins/:(admin_id)',
            'action': 'updateAdmin',
            'method': ['PUT'],
        },
        {
            'name': 'deleteAdmin',
            'path': '/v1/admins/:(admin_id)',
            'action': 'deleteAdmin',
            'method': ['DELETE'],
        },
        {
            'name': 'authenticate',
            'path': '/v1/authenticate/:(username)',
            'action': 'authenticate',
            'method': ['POST'],
        },
    ]

    @authentication_required()
    @cherrypy.tools.json_out()
    def getAdmin(self, admin_id):
        """ Get an admin by name """

        try:
            admin = self.app.admin_api.getAdminById(
                cherrypy.request.db, admin_id)

            response = {
                'admin': admin.getCleanDict(),
            }
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def getAdminList(self):
        """ Return list of admin users """

        try:
            adminList = self.app.admin_api.getAdminList(cherrypy.request.db)

            response = {
                'admins': adminList.getCleanDict(),
            }
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addAdmin(self):
        """
        Add a new admin to the system
        """

        response = None

        postdata = cherrypy.request.json

        if 'admin' not in postdata:
            raise cherrypy.HTTPError(400)

        adminRequestObject = Admin.getFromDict(postdata['admin'])

        isCrypted = str2bool(postdata['isCrypted'])

        try:
            self.app.admin_api.addAdmin(
                cherrypy.request.db,
                adminRequestObject.getUsername(),
                adminRequestObject.getPassword(),
                isCrypted,
                adminRequestObject.getRealname(),
                adminRequestObject.getDescription())
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def deleteAdmin(self, admin_id):
        """ Delete an existing admin from the system """

        response = None

        try:
            self.app.admin_api.deleteAdmin(cherrypy.request.db, admin_id)
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def updateAdmin(self, admin_id):
        """
        Update an existing admin in the system
        """

        postdata = cherrypy.request.json

        admin = Admin.getFromDict(postdata['admin'])

        admin.setId(admin_id)

        isCrypted = postdata['isCrypted'][0].lower() == 't' \
            if 'isCrypted' in postdata and postdata['isCrypted'] else False

        try:
            self.app.admin_api.updateAdmin(
                cherrypy.request.db, admin, isCrypted)

            response = None
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def authenticate(self, username, password):
        """
        Check if a username / password combo matches a user in the system
        """

        password_auth = UsernamePasswordAuthenticationMethod()
        password_auth.session = cherrypy.request.db
        try:
            password_auth.authenticate(username=username, password=password)
            valid_user = self.app.admin_api.getAdmin(
                cherrypy.request.db, username)
            response = {
                'authenticate': valid_user,
            }
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
