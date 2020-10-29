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
import time
import traceback
from typing import TYPE_CHECKING

import cherrypy

from tortuga.node.manager import NodeStoreManager
from tortuga.web_service.auth.decorators import authentication_required
from .base import Controller, HttpError, HttpNotFoundError

if TYPE_CHECKING:
    from tortuga.node.types import Node


class NodeController(Controller):
    """
    Node web service controller class.

    """
    name = 'nodes'
    type_store = NodeStoreManager.get()
    methods = ['GET', 'PUT']


class NodeStatusController(Controller):
    name = 'node_status'
    type_store = NodeStoreManager.get()
    methods = ['GET', 'PUT']

    @property
    def actions(self):
        actions = [
            {
                'name': '{}_get'.format(self.name),
                'path': '/v2/{}/:(obj_id)/status'.format(NodeController.name),
                'method': ['GET'],
                'action': 'get',
            },
            {
                'name': '{}_update'.format(self.name),
                'path': '/v2/{}/:(obj_id)/status'.format(NodeController.name),
                'method': ['PUT'],
                'action': 'update',
            },
        ]
        return actions

    def marshall(self, obj: 'Node') -> dict:
        schema_class = self.type_store.status_type_class.schema_class
        marshalled = schema_class().dump(obj)
        return marshalled.data

    @authentication_required()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self, obj_id: str) -> dict:
        try:
            # Get full Node object
            obj_current = self.type_store.get(obj_id)
            if not obj_current:
                raise HttpNotFoundError('Not found: {}'.format(obj_id))

            # Convert request to Node object (will be incomplete)
            obj = self.unmarshall(cherrypy.request.json)

            # Make sure the object IDs match
            if obj_current.id != obj.id:
                raise HttpError('Object ID mismatch')

            # Update the current object with the state from the request;
            # if state is not provided, keep the current state
            obj_current.state = obj.state or obj_current.state
            obj_current.last_update = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.gmtime(time.time())
            )
            obj = self.type_store.save(obj_current)
            response = self.marshall(obj)
        except HttpError as ex:
            response = self.error_response(str(ex), http_status=ex.status_code)
        except Exception as ex:
            self._logger.error(traceback.format_exc())
            response = self.error_response(str(ex))
        return self.format_response(response)
