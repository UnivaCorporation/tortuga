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

import http.client
import logging
from sys import exc_info

import cherrypy

from tortuga.exceptions.internalError import InternalError
from tortuga.utility import tortugaStatus
from tortuga.types.application import Application


class TortugaController(object):
    """
    Base controller class.

    """
    #
    # A list of actions, each action being defined as follows:
    #
    #    {
    #        'name':   'example_name',
    #        'url':    '/path/to/action/',
    #        'action': 'actionMethodName'
    #        'method': ['GET', 'POST', ...]
    #    }
    #
    actions = []
    app = Application()

    def __init__(self):
        self._logger = logging.getLogger(
            'tortuga.web_service.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

    def getLogger(self):
        return self._logger

    @classmethod
    def addTortugaResponseHeaders(cls, status, msg='Success'):
        cherrypy.response.headers['Tortuga-Status-Code'] = status
        cherrypy.response.headers['Tortuga-Status-Message'] = msg

    @classmethod
    def handleCpException(cls):
        cherrypy.response.status = http.client.BAD_REQUEST

        ex = exc_info()[1]

        if ex is None:
            ex = InternalError('Internal Webservice Error')

        cls.handleException(ex)

    @classmethod
    def getTortugaStatusCode(cls, ex):
        exClass = ex.__class__.__name__.split('.')[-1]

        for code in tortugaStatus.exceptionMap.keys():
            exStr = tortugaStatus.exceptionMap.get(code).split('.')[-1]
            if exStr == exClass:
                status = code
                break
        else:
            status = tortugaStatus.TORTUGA_ERROR

        return status

    @classmethod
    def handleException(cls, ex):
        status = cls.getTortugaStatusCode(ex)

        cls.addTortugaResponseHeaders(status, str(ex))

    def formatResponse(self, response=None): \
            # pylint: disable=no-self-use
        if response is not None:
            return response

        cherrypy.response.status = http.client.NO_CONTENT

        return ''

    def errorResponse(self, msg, code=None, http_status=http.client.BAD_REQUEST): \
            # pylint: disable=no-self-use
        response = {
            'error': {
                'message': msg,
            }
        }

        if code is not None:
            response['error']['code'] = code

        cherrypy.response.status = http_status

        return response

    def notFoundErrorResponse(self, msg, code=None):
        """Return HTTP status 404 for 'not found' exceptions"""

        return self.errorResponse(msg, code=code,
                                  http_status=http.client.NOT_FOUND)
