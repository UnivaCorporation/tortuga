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

import cherrypy

from tortuga.addhost.addHostManager import AddHostManager
from tortuga.db.models.nodeRequest import NodeRequest
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.schema import NodeSchema
from tortuga.utility.helper import str2bool

from .. import app
from ..threadManager import threadManager
from ..auth import authentication_required
from .common import make_options_from_query_string, parse_tag_query_string
from .tortugaController import TortugaController


class NodeController(TortugaController):
    """
    Admin node controller class.

    """
    actions = [
        {
            'name': 'getNodeList',
            'path': '/v1/nodes/',
            'action': 'getNodes',
            'method': ['GET']
        },
        {
            'name': 'getNodeProvisioningInfo',
            'path': '/v1/nodes/:(nodeName)/provisioningInfo',
            'action': 'getNodeProvisioningInfo',
            'method': ['GET']
        },
        {
            'name': 'getNodeById',
            'path': '/v1/nodes/:(node_id)',
            'action': 'getNodeById',
            'method': ['GET']
        },
        {
            'name': 'setParentNode',
            'path': '/v1/nodes/:nodeName/parentNode',
            'action': 'setParentNode',
            'method': ['POST'],
        },
        {
            'name': 'idleNode',
            'path': '/v1/nodes/:nodeName/idle',
            'action': 'idleNode',
            'method': ['GET'],
        },
        {
            'name': 'activateNode',
            'path': '/v1/nodes/:nodeName/activate',
            'action': 'activateNode',
            'method': ['POST'],
        },
        {
            'name': 'checkpointNode',
            'path': '/v1/nodes/:nodeName/checkpoint',
            'action': 'checkpointNode',
            'method': ['GET'],
        },
        {
            'name': 'revertNodeToCheckpoint',
            'path': '/v1/nodes/:nodeName/revert',
            'action': 'revertNodeToCheckpoint',
            'method': ['GET'],
        },
        {
            'name': 'migrateNode',
            'path': '/v1/nodes/:nodeName/migrate/:(remainingNodeList)'
                    '/type/:(liveMigrate)',
            'action': 'migrateNode',
            'method': ['GET'],
        },
        {
            'name': 'startupNode',
            'path': '/v1/nodes/:nodeName/startup/:(nodeString)'
                    '/boot/:(bootMethod)',
            'action': 'startupNode',
            'method': ['PUT'],
        },
        {
            'name': 'evacuateChildren',
            'path': '/v1/nodes/:nodeName/evacuate',
            'action': 'evacuateChildren',
            'method': ['GET'],
        },
        {
            'name': 'getChildrenList',
            'path': '/v1/nodes/:nodeName/children',
            'action': 'getChildrenList',
            'method': ['GET'],
        },
        {
            'name': 'shutdownNode',
            'path': '/v1/nodes/:nodeName/shutdown',
            'action': 'shutdownNode',
            'method': ['GET'],
        },
        {
            'name': 'resetNode',
            'path': '/v1/nodes/:nodeName/reset',
            'action': 'rebootNode',
            'method': ['PUT'],
        },
        {
            'name': 'deleteNode',
            'path': '/v1/nodes/:(name)',
            'action': 'deleteNode',
            'method': ['DELETE'],
        },
        {
            'name': 'adminNodeStatus',
            'path': '/v1/nodes/:(name)',
            'action': 'updateNodeRequest',
            'method': ['PUT'],
        },
    ]

    @cherrypy.tools.json_out()
    @authentication_required()
    def getNodes(self, **kwargs):
        """
        Return list of all available nodes

        """

        tagspec = []

        if 'tag' in kwargs and kwargs['tag']:
            tagspec.extend(parse_tag_query_string(kwargs['tag']))

        try:
            options = make_options_from_query_string(
                kwargs['include']
                if 'include' in kwargs else None,
                ['softwareprofile', 'hardwareprofile'])

            if 'addHostSession' in kwargs and kwargs['addHostSession']:
                nodeList = app.node_api.getNodesByAddHostSession(
                    kwargs['addHostSession'], options)
            elif 'name' in kwargs and kwargs['name']:
                nodeList = app.node_api.getNodesByNameFilter(
                    kwargs['name'], optionDict=options)
            elif 'installer' in kwargs and str2bool(kwargs['installer']):
                nodeList = TortugaObjectList(
                    [app.node_api.getInstallerNode()]
                )
            elif 'ip' in kwargs:
                nodeList = TortugaObjectList(
                    [app.node_api.getNodeByIp(kwargs['ip'])])
            else:
                nodeList = app.node_api.getNodeList(tags=tagspec)

            response = {
                'nodes': NodeSchema().dump(nodeList, many=True).data
            }
        except Exception as ex:
            self.getLogger().exception('node WS API getNodes() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def getNodeById(self, node_id: str, **kwargs):
        """
        Return node information

        """
        try:
            options = make_options_from_query_string(
                kwargs['include']
                if 'include' in kwargs else None,
                ['softwareprofile', 'hardwareprofile'])

            node = app.node_api.getNodeById(node_id, optionDict=options)

            response = {
                'node': node.getCleanDict(),
            }
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API getNodeById() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def updateNodeRequest(self, name):
        postdata = cherrypy.request.json

        state = postdata['state'] if 'state' in postdata else None

        try:
            # If 'bootFrom' is not an int value, this will raise ValueError
            bootFrom = int(postdata['bootFrom']) \
                if 'bootFrom' in postdata and \
                postdata['bootFrom'] is not None else None

            result = app.node_api.updateNodeStatus(name, state, bootFrom)

            response = {
                'changed': result,
            }
        except Exception as ex:
            self.getLogger().exception(
                'node WS API updateNodeRequest() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getNodeProvisioningInfo(self, nodeName):
        """
        Return provisioning information for a node
        """

        try:
            info = app.node_api.getProvisioningInfo(nodeName)

            response = {
                'provisioninginfo': info.getCleanDict(),
            }
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception(
                'node WS API getNodeProvisioningInfo() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def setParentNode(self, nodeName, parentNodeName):
        """
        Handle POST to /nodes/:(nodeName)/parentNode

        Required data: parentNodeName
        """

        response = None

        postdata = cherrypy.request.json

        if 'parentNodeName' not in postdata or \
                not postdata['parentNodeName']:
            raise InvalidArgument(
                'Missing or empty required field: [%s]' % (
                    'parentNodeName'))

        try:
            app.node_api.setParentNode(nodeName, parentNodeName)
        except Exception as ex:
            self.getLogger().exception('node WS API setParentNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def idleNode(self, nodeName):
        """
        Idle an active node
        """

        try:
            response = app.node_api.idleNode(nodeName)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API idleNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def activateNode(self, nodeName):
        """
        Activate an idle node
        """

        if int(cherrypy.request.headers['Content-Length']):
            postdata = cherrypy.request.json

            softwareProfileName = postdata['softwareProfileName'] \
                if 'softwareProfileName' in postdata else None
        else:
            softwareProfileName = None

        try:
            response = app.node_api.activateNode(nodeName, softwareProfileName)

        except Exception as ex:
            self.getLogger().exception('node WS API activateNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def checkpointNode(self, nodeName):
        """
        Checkpoint a node
        """

        response = None

        try:
            app.node_api.checkpointNode(nodeName)
        except Exception as ex:
            self.getLogger().exception('node WS API checkpointNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def revertNodeToCheckpoint(self, nodeName):
        """
        Migrate a node
        """

        response = None

        try:
            app.node_api.revertNodeToCheckpoint(nodeName)
        except Exception as ex:
            self.getLogger().exception(
                'node WS API revertNodeToCheckpoint() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def migrateNode(self, nodeName: str, remainingNodeString: str,
                    liveMigrate: str):
        """
        Migrate a node
        """

        response = None

        try:
            # Make remainingNodeString into a real list
            remainingNodeList = [
                node for node in remainingNodeString.split('+')]

            app.node_api.migrateNode(
                nodeName, remainingNodeList, str2bool(liveMigrate))
        except Exception as ex:
            self.getLogger().exception('node WS API migrateNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def startupNode(self, nodeName, nodeString, bootMethod):
        response = None

        try:
            # Make node list
            nodeList = [node for node in nodeString.split('+')] \
                if nodeString != '+' else []

            app.node_api.startupNode(nodeName, nodeList, bootMethod)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API startupNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def evacuateChildren(self, nodeName):
        response = None

        try:
            app.node_api.evacuateChildren(nodeName)
        except Exception as ex:
            self.getLogger().exception('node WS API evacuateChildren() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getChildrenList(self, nodeName):
        """
        Return list of all children nodes
        """

        try:
            nodeList = app.node_api.getChildrenList(nodeName)

            response = nodeList.getCleanDict()
        except Exception as ex:
            self.getLogger().exception('node WS API getChildrenList() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def shutdownNode(self, nodeName):
        response = None

        try:
            app.node_api.shutdownNode(nodeName)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API shutdownNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def rebootNode(self, nodeName, **kwargs):
        response = None

        soft_reset = not str2bool(kwargs['hard']) \
            if 'hard' in kwargs else True

        reinstall = str2bool(kwargs['reinstall']) \
            if 'reinstall' in kwargs else False

        try:
            app.node_api.rebootNode(
                nodeName, bSoftReset=soft_reset, bReinstall=reinstall)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API rebootNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def transferNode(self, softwareProfileName, nodeName,
                     srcSoftwareProfileName, nodeCount):
        try:
            nodeList = app.node_api.transferNode(
                softwareProfileName, nodeName, srcSoftwareProfileName,
                nodeCount)

            response = nodeList.getCleanDict()
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API transferNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))
        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def addStorageVolume(self, nodeName, volume):
        response = None

        postdata = cherrypy.request.json

        bDirect = postdata['isDirect'] if 'isDirect' in postdata else None

        try:
            app.node_api.addStorageVolume(nodeName, volume, bDirect)
        except Exception as ex:
            self.getLogger().exception('node WS API addStorageVolume() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def removeStorageVolume(self, nodeName, volume):
        response = None

        try:
            app.node_api.removeStorageVolume(
                nodeName, volume)
        except Exception as ex:
            self.getLogger().exception(
                'node WS API removeStorageVolume() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getStorageVolumeList(self, nodeName):
        try:
            result = app.node_api.getStorageVolumeList(nodeName)

            response = result.getCleanDict()
        except Exception as ex:
            self.getLogger().exception(
                'node WS API getStorageVolumeList() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def deleteNode(self, name):
        """
        Handle /nodes/:(name) (DELETE)
        """

        try:
            transaction_id = enqueue_delete_hosts_request(
                cherrypy.request.db, name)

            self.getLogger().debug(
                'NodeController.deleteNode(): delete request queued: %s' % (
                    transaction_id))

            response = dict(transaction_id=transaction_id)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception('node WS API deleteNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)


def enqueue_delete_hosts_request(session, nodespec):
    request = init_node_request_record(nodespec)

    session.add(request)

    session.commit()

    threadManager.queue.put({
        'action': 'DELETE',
        'data': {
            'transaction_id': request.addHostSession,
            'nodespec': nodespec,
        },
    })

    return request.addHostSession


def init_node_request_record(nodespec):
    request = NodeRequest(nodespec)
    request.timestamp = datetime.datetime.utcnow()
    request.addHostSession = AddHostManager().createNewSession()
    request.action = 'DELETE'

    return request
