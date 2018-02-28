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

# pylint: disable=W0703

import base64
import cherrypy

from tortuga.web_service.ruleManager import ruleManager
from tortuga.exceptions.invalidArgument import InvalidArgument
from .tortugaController import TortugaController
from .authController import AuthController, require


class ApplicationMonitorController(TortugaController):
    """
    Application monitor admin controller class.

    """
    actions = [
        {
            'name': 'applicationMonitorAdmin',
            'path': '/v1/applications/:(application_name)/data',
            'action': 'receiveApplicationData',
            'method': ['POST'],
        },
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def receiveApplicationData(self, application_name):
        """ Receive application monitoring data. """

        response = None

        self.getLogger().debug(
            '[%s] Received data for: %s' % (
                self.__module__, application_name))

        try:
            postdata = cherrypy.request.json

            if 'data' not in postdata:
                raise InvalidArgument('Malformed application data')

            applicationData = base64.decodestring(
                base64.b64decode(postdata['data']))

            ruleManager.receiveApplicationData(
                application_name, applicationData)
        except TypeError:
            errmsg = 'Malformed data payload (base64 decode failed)'
            self.getLogger().debug(
                '[%s] receiveApplicationData(): %s' % (
                    self.__module__, errmsg))
            response = self.errorResponse(errmsg)
        except Exception as ex:
            self.getLogger().debug('[%s] %s' % (self.__module__, ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
