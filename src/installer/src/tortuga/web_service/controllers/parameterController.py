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

from tortuga.exceptions.parameterAlreadyExists import ParameterAlreadyExists
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.objects.parameter import Parameter
from tortuga.web_service.auth.decorators import authentication_required
from .tortugaController import TortugaController


class ParameterController(TortugaController):
    """
    Admin parameter controller class.

    """
    actions = [
        {
            'name': 'userParameter',
            'path': '/v1/parameters/:(name)',
            'action': 'getParameter',
            'method': ['GET']
        },
        {
            'name': 'userParameterList',
            'path': '/v1/parameters/',
            'action': 'getParameterList',
            'method': ['GET']
        },
        {
            'name': 'createParameter',
            'path': '/v1/parameters/',
            'action': 'createParameter',
            'method': ['POST']
        },
        {
            'name': 'updateParameter',
            'path': '/v1/parameters/:(name)',
            'action': 'updateParameter',
            'method': ['PUT']
        },
        {
            'name': 'deleteParameter',
            'path': '/v1/parameters/:(name)',
            'action': 'deleteParameter',
            'method': ['DELETE']
        },
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getParameter(self, name):
        """
        Return info for the specified parameter.

        """
        try:
            parameter = self.app.parameter_api.getParameter(
                cherrypy.request.db, name)

            response = {
                'globalparameter': parameter.getCleanDict(),
            }
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getParameterList(self):
        """
        Return all known parameters.

        """
        self._logger.debug('Retrieving parameter list')

        try:
            parameterList = self.app.parameter_api.getParameterList(
                cherrypy.request.db
            )

            response = {
                'globalparameters': parameterList.getCleanDict(),
            }
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def createParameter(self):
        """
        Creates a parameter.

        """
        self._logger.debug('Creating parameter')

        postdata = cherrypy.request.json
        parameter = Parameter.getFromDict(postdata)

        try:
            self.app.parameter_api.getParameter(
                cherrypy.request.db, parameter.getName())
            parameter_exists = True

        except ParameterNotFound:
            parameter_exists = False

        try:
            if parameter_exists:
                raise ParameterAlreadyExists()

            self.app.parameter_api.upsertParameter(
                cherrypy.request.db, parameter)

            response = None

        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def updateParameter(self, name):
        """
        Creates or updates a parameter.

        """
        self._logger.debug('Creating/updating parameter: {}'.format(name))

        postdata = cherrypy.request.json
        parameter = Parameter.getFromDict(postdata)

        try:
            if name != parameter.getName():
                raise Exception('Parameter name mismatch')

            self.app.parameter_api.upsertParameter(
                cherrypy.request.db, parameter)
            response = None

        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)


    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def deleteParameter(self, name):
        """
        Deletes a parameter.

        """
        self._logger.debug('Deleting parameter: {}'.format(name))

        try:
            self.app.parameter_api.deleteParameter(
                cherrypy.request.db, name)
            response = None

        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
