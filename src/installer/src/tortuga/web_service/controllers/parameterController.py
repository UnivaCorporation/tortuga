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

from .tortugaController import TortugaController
from .authController import AuthController, require
from .. import app


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
            'path': '/v1/parameters',
            'action': 'getParameterList',
            'method': ['GET']
        },
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def getParameter(self, name):
        """ Return info for the specified parameter. """

        # self.getLogger().debug('Retrieving parameter [%s]' % (name))

        try:
            parameter = app.parameter_api.getParameter(name)

            response = {
                'globalparameter': parameter.getCleanDict(),
            }
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def getParameterList(self):
        """ Return all known parameters. """

        self.getLogger().debug('Retrieving parameter list')

        try:
            parameterList = app.parameter_api.getParameterList()

            response = {
                'globalparameters': parameterList.getCleanDict(),
            }
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
