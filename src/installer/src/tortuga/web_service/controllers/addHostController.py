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

import datetime
import json

import cherrypy
from marshmallow import Schema, fields

from tortuga.addhost.addHostManager import AddHostManager
from tortuga.addhost.utility import validate_addnodes_request
from tortuga.db.models.nodeRequest import NodeRequest
from tortuga.db.nodeRequestsDbHandler import NodeRequestsDbHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.notFound import NotFound

from .. import dbm
from ..threadManager import threadManager
from .authController import AuthController, require
from .tortugaController import TortugaController


class NodeRequestSchema(Schema):
    id = fields.Integer()
    request = fields.String()
    timestamp = fields.DateTime()
    last_update = fields.DateTime()
    state = fields.String()
    addHostSession = fields.String()
    message = fields.String()
    admin_id = fields.Integer()
    action = fields.String()


class AddHostController(TortugaController):
    actions = [
        {
            'name': 'addHostGetStatus',
            'path': '/v1/addhost/:(session)/status',
            'action': 'getStatus',
            'method': ['GET']
        },
        {
            'name': 'addNodes',
            'path': '/v1/nodes/',
            'action': 'addNodes',
            'method': ['POST']
        },
        {
            'name': 'getAddHostRequests',
            'path': '/v1/addhost/requests/',
            'action': 'getAddHostRequests',
            'method': ['GET'],
        },
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def addNodes(self):
        response = None

        try:
            if 'node' not in cherrypy.request.json:
                raise InvalidArgument('Malformed request')

            addNodesRequest = {
                'addNodesRequest': cherrypy.request.json['node'],
            }

            admin_id = cherrypy.session.get('admin_id')
            if admin_id:
                addNodesRequest['metadata'] = {
                    'admin_id': admin_id,
                }

            response = {
                'addHostSession': enqueue_addnodes_request(
                    cherrypy.request.db, addNodesRequest),
            }
        except Exception as ex:
            self.getLogger().exception('Exception occurred while adding hosts')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def getStatus(self, session, **kwargs):
        '''
        Call the addHost manager directly
        '''

        startMessage = int(kwargs['startMessage']) \
            if 'startMessage' in kwargs else 0

        getNodes = kwargs['getNodes'].lower().startswith('t') \
            if 'getNodes' in kwargs else False

        try:
            status = AddHostManager().getStatus(
                session, int(startMessage), getNodes)

            response = {'addhoststatus': status.getCleanDict()}
        except NotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().error('Exception retrieving addhost status')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @require()
    def getAddHostRequests(self, **kwargs):
        try:
            if 'addHostSession' in kwargs:
                add_host_request = \
                    NodeRequestsDbHandler().get_by_addHostSession(
                        cherrypy.request.db, kwargs['addHostSession'])
                if not add_host_request:
                    return self.formatResponse(response=[])

                result = [add_host_request]
            else:
                result = NodeRequestsDbHandler().get_all(cherrypy.request.db)

            response = NodeRequestSchema().dump(result, many=True).data
        except Exception as ex:
            self.getLogger().error('Exception retrieving add host request(s)')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)


def enqueue_addnodes_request(session, addNodesRequest):
    validate_addnodes_request(addNodesRequest['addNodesRequest'])

    request = init_node_request_record(addNodesRequest)

    session.add(request)

    session.commit()

    threadManager.queue.put({
        'action': 'ADD',
        'data': {
            'addHostSession': request.addHostSession,
        },
    })

    return request.addHostSession


def init_node_request_record(addNodesRequest):
    request = NodeRequest(json.dumps(addNodesRequest['addNodesRequest']))
    request.timestamp = datetime.datetime.utcnow()
    request.addHostSession = AddHostManager().createNewSession()
    request.action = 'ADD'

    if 'metadata' in addNodesRequest and \
            'admin_id' in addNodesRequest['metadata']:
        request.admin_id = addNodesRequest['metadata']['admin_id']

    return request
