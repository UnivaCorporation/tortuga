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
import traceback
from typing import Any, List

import cherrypy

from tortuga.logging import WEBSERVICE_NAMESPACE
from tortuga.types.base import BaseType
from tortuga.typestore.base import TypeStore
from tortuga.web_service.auth.decorators import authentication_required


class Controller(object):
    """
    Base controller class.

    """
    name: str = None
    methods: List[str] = ['GET']
    type_store: TypeStore = None

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
                'path': '/v2/{}/:(obj_id)'.format(self.name),
                'method': ['GET'],
                'action': 'get'
            })

        if 'POST' in self.methods:
            #
            # Action for creating an object
            #
            actions.append({
                'name': '{}_create'.format(self.name),
                'path': '/v2/{}/'.format(self.name),
                'method': ['POST'],
                'action': 'create'
            })

        if 'PUT' in self.methods:
            #
            # Action for updating an object
            #
            actions.append({
                'name': '{}_update'.format(self.name),
                'path': '/v2/{}/:(obj_id)'.format(self.name),
                'method': ['PUT'],
                'action': 'update'
            })

        if 'DELETE' in self.methods:
            #
            # Action for updating an object
            #
            actions.append({
                'name': '{}_delete'.format(self.name),
                'path': '/v2/{}/:(obj_id)'.format(self.name),
                'method': ['DELETE'],
                'action': 'delete'
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

    def marshall(self, obj: BaseType) -> dict:
        """
        Marshalls a obj into a dict.

        :param BaseType obj: the obj instance to marshall

        :return dict: the marshalled data

        """
        schema_class = obj.get_schema_class()
        marshalled = schema_class().dump(obj)
        return marshalled.data

    def unmarshall(self, obj_dict: dict) -> BaseType:
        """
        Unmarshalls an obj dict into an obj class instance.

        :param dict obj_dict:
        :return BaseType: the unmarshalled obj

        """
        schema_class = self.type_store.type_class.get_schema_class()
        unmarshalled = schema_class().load(obj_dict)
        return self.type_store.type_class(**unmarshalled.data)

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
            for obj in self.type_store.list(**params):
                response.append(self.marshall(obj))

        except Exception as ex:
            self._logger.error(traceback.format_exc())
            response = self.error_response(str(ex))

        return self.format_response(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def get(self, obj_id: str) -> dict:
        """
        Gets a single object, by id.

        :param str obj_id: the id of the object to get

        :return dict: the object, in dict form

        """
        try:
            obj = self.type_store.get(obj_id)
            response = self.marshall(obj)

        except Exception as ex:
            self._logger.error(traceback.format_exc())
            response = self.error_response(str(ex))

        return self.format_response(response)

    @authentication_required()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self) -> dict:
        """
        Creates a single object.

        :return str: the object, in dict form

        """
        try:
            obj = self.unmarshall(cherrypy.request.json)
            obj = self.type_store.save(obj)
            response = self.marshall(obj)

        except Exception as ex:
            self._logger.error(traceback.format_exc())
            response = self.error_response(str(ex))

        return self.format_response(response)

    @authentication_required()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self, obj_id: str) -> dict:
        try:
            obj = self.unmarshall(cherrypy.request.json)
            obj = self.type_store.save(obj)
            response = self.marshall(obj)

        except Exception as ex:
            self._logger.error(traceback.format_exc())
            response = self.error_response(str(ex))

        return self.format_response(response)

    @authentication_required()
    def delete(self, obj_id: str):
        try:
            self.type_store.delete(obj_id)
            response = None

        except Exception as ex:
            self._logger.error(traceback.format_exc())
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
