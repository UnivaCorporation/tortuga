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
from typing import Any, List

import cherrypy

from tortuga.logging import WEBSERVICE_NAMESPACE
from tortuga.web_service.auth.decorators import authentication_required


class Controller(object):
    """
    Base controller class.

    """
    name = None
    methods = ['GET']
    object_store = None

    def __init__(self):
        self._logger = logging.getLogger(WEBSERVICE_NAMESPACE)

    @property
    def actions(self):
        actions = []

        if 'GET' in self.methods:
            #
            # Action for listing objects
            #
            actions.append({
                'name': '{}_list'.format(self.name),
                'path': '/v2/{}/'.format(self.name),
                'method': ['GET'],
                'action': 'list'
            })

            #
            # Action for getting a single object
            #
            actions.append({
                'name': '{}_get'.format(self.name),
                'path': '/v2/{}/:(id)'.format(self.name),
                'method': ['GET'],
                'action': 'get'
            })

        return actions

    def build_params(self, query: dict) -> dict:
        """
        Takes a list of query params and transforms them into parameters
        that are safe for passing to an object store method.

        :param dict query: the HTTP query parameters

        :return dict: the transformed method parameters

        """
        params = {}

        for k, v in query.items():
            #
            # true/false values should be converted to python True/False
            #
            if v.strip().lower() == 'true':
                params[k] = True
            elif v.strip().lower() == 'false':
                params[k] = False
            #
            # The limit keyword should always be an integer
            #
            elif k == 'limit':
                params[k] = int(v)
            else:
                params[k] = v

        return params

    @authentication_required()
    @cherrypy.tools.json_out()
    def list(self, **query) -> List[dict]:
        """
        Gets a list of objects from the configured object store.

        :param query: query parameters

        :return List[dict]: a list of objects, in dict form

        """
        try:
            params = self.build_params(query)

            response = []
            for obj in self.object_store.list(**params):
                if hasattr(obj, 'schema'):
                    response.append(obj.schema().dump(obj).data)
                else:
                    response.append(obj)

        except Exception as ex:
            self._logger.error(str(ex))
            response = self.error_response(str(ex))

        return self.format_response(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def get(self, id: str) -> dict:
        """
        Gets a single object, by id.

        :param str id: the id of the object to get

        :return dict: the object, in dict form

        """
        try:
            obj = self.object_store.get(id)
            if hasattr(obj, 'schema'):
                response = obj.schema().dump(obj).data
            else:
                response = obj

        except Exception as ex:
            self._logger.error(str(ex))
            response = self.error_response(str(ex))

        return self.format_response(response)

    def format_response(self, response: Any = None) -> Any:
        """
        Prepares a response for output.

        :param Any response: the response to prepare

        :return Any: the prepared response

        """
        if response is not None:
            return response
        cherrypy.response.status = http.client.NO_CONTENT
        return ''

    def error_response(self, msg: str,
                       http_status=http.client.BAD_REQUEST) -> dict:
        """
        Prepares an error response.

        :param msg:         the error message
        :param http_status: the HTTP status code

        :return: the prepared error response

        """
        response = {
            'error': {
                'message': msg,
            }
        }
        cherrypy.response.status = http_status
        return response
