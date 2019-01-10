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

from marshmallow import Schema, ValidationError, fields, validates

import cherrypy
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.nodeTransferNotValid import NodeTransferNotValid
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.node.task import enqueue_delete_hosts_request
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.schema import NodeSchema
from tortuga.utility.helper import str2bool
from tortuga.web_service.auth.decorators import authentication_required

from .common import make_options_from_query_string, parse_tag_query_string
from .tortugaController import TortugaController


class UpdateNodeRequestSchema(Schema):
    state = fields.String(255)
    bootFrom = fields.Integer()

    @validates('bootFrom')
    def validates_bootFrom(self, value):
        if value not in (0, 1):
            raise ValidationError(
                'bootFrom must be 0 (disk) or 1 (network)'
            )


class TransferNodesRequestSchema(Schema):
    srcSoftwareProfile = fields.String(255)
    dstSoftwareProfile = fields.String(255, required=True)
    count = fields.Integer()
    bForce = fields.Boolean(default=False)


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
            'name': 'startupNode',
            'path': '/v1/nodes/:nodeName/startup/:(nodeString)'
                    '/boot/:(bootMethod)',
            'action': 'startupNode',
            'method': ['PUT'],
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
            'path': '/v1/nodes/:(nodespec)',
            'action': 'deleteNode',
            'method': ['DELETE'],
        },
        {
            'name': 'adminNodeStatus',
            'path': '/v1/nodes/:(name)',
            'action': 'updateNodeRequest',
            'method': ['PUT'],
        },
        {
            'name': 'getNodeByIpRequest',
            'path': '/v1/identify-node',
            'action': 'getNodeByIpRequest',
            'method': ['GET']
        },
        {
            'name': 'transferNodes',
            'path': '/v1/transfer-nodes/',
            'action': 'transferNodes',
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
                nodeList = self.app.node_api.getNodesByAddHostSession(
                    cherrypy.request.db, kwargs['addHostSession'], options)
            elif 'name' in kwargs and kwargs['name']:
                nodeList = self.app.node_api.getNodesByNameFilter(
                    cherrypy.request.db, kwargs['name'], optionDict=options)
            elif 'installer' in kwargs and str2bool(kwargs['installer']):
                nodeList = TortugaObjectList(
                    [self.app.node_api.getInstallerNode(cherrypy.request.db)]
                )
            elif 'ip' in kwargs:
                nodeList = TortugaObjectList(
                    [self.app.node_api.getNodeByIp(
                        cherrypy.request.db, kwargs['ip'])])
            else:
                nodeList = self.app.node_api.getNodeList(
                    cherrypy.request.db, tags=tagspec)

            response = {
                'nodes': NodeSchema().dump(nodeList, many=True).data
            }
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API getNodes() failed')
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

            node = self.app.node_api.getNodeById(
                cherrypy.request.db, node_id, optionDict=options)

            response = {
                'node': node.getCleanDict(),
            }
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # pylint: disable=broad-except
            self._logger.exception('node WS API getNodeById() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getNodeByIpRequest(self):
        ip = cherrypy.request.remote.ip

        try:
            if ip in ('127.0.0.1', '::1'):
                node = self.app.node_api.getInstallerNode(cherrypy.request.db)
            else:
                node = self.app.node_api.getNodeByIp(cherrypy.request.db, ip)

            response = {'node': node.getCleanDict()}
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(
                'node WS API gRequest() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def updateNodeRequest(self, name):
        try:
            request_data, errors = \
                UpdateNodeRequestSchema().load(cherrypy.request.json)
            if not errors:
                result = self.app.node_api.updateNodeStatus(
                    cherrypy.request.db,
                    name,
                    request_data['state']
                    if 'state' in request_data else None,
                    request_data['bootFrom']
                    if 'bootFrom' in request_data else None
                )

                response = {
                    'changed': result,
                }
            else:
                buf = 'Invalid argument(s): '

                for field, messages in errors.items():
                    buf += '%s: %s' % (field, ', '.join(messages))

                raise InvalidArgument(buf)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(
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
            info = self.app.node_api.getProvisioningInfo(
                cherrypy.request.db, nodeName)

            response = {
                'provisioninginfo': info.getCleanDict(),
            }
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(
                'node WS API getNodeProvisioningInfo() failed')
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
            response = self.app.node_api.idleNode(
                cherrypy.request.db, nodeName)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API idleNode() failed')
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

        postdata = cherrypy.request.json

        softwareProfileName = postdata['softwareProfileName'] \
            if 'softwareProfileName' in postdata else None

        try:
            response = self.app.node_api.activateNode(
                cherrypy.request.db, nodeName, softwareProfileName)

        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API activateNode() failed')
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

            self.app.node_api.startupNode(
                cherrypy.request.db, nodeName, nodeList, bootMethod)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API startupNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def shutdownNode(self, nodeName):
        response = None

        try:
            self.app.node_api.shutdownNode(cherrypy.request.db, nodeName)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API shutdownNode() failed')
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
            self.app.node_api.rebootNode(
                cherrypy.request.db, nodeName, bSoftReset=soft_reset,
                bReinstall=reinstall)
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API rebootNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @authentication_required()
    def transferNodes(self, **kwargs):
        try:
            request_data, errors = \
                TransferNodesRequestSchema().load(cherrypy.request.json)
            if errors:
                buf = 'Invalid argument(s): '

                for field, messages in errors.items():
                    buf += '%s: %s' % (field, ', '.join(messages))

                raise InvalidArgument(buf)

            nodespec = kwargs.get('nodespec')

            self.app.node_api.transferNodes(
                cherrypy.request.db,
                request_data['dstSoftwareProfile'],
                count=request_data['count'] if not nodespec else None,
                bForce=request_data.get('bForce', False),
                nodespec=nodespec,
                srcSoftwareProfile=request_data.get('srcSoftwareProfile'),
            )

            response = None
        except NodeNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except NodeTransferNotValid as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.errorResponse(str(ex))
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(str(ex))
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
            self.app.node_api.addStorageVolume(
                nodeName, volume, bDirect)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API addStorageVolume() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def removeStorageVolume(self, nodeName, volume):
        response = None

        try:
            self.app.node_api.removeStorageVolume(
                nodeName, volume)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(
                'node WS API removeStorageVolume() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getStorageVolumeList(self, nodeName):
        try:
            result = self.app.node_api.getStorageVolumeList(
                cherrypy.request.db, nodeName)

            response = result.getCleanDict()
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception(
                'node WS API getStorageVolumeList() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def deleteNode(self, nodespec, **kwargs):
        """
        Handle /nodes/:(nodespec) (DELETE)
        """

        try:
            transaction_id = enqueue_delete_hosts_request(
                cherrypy.request.db,
                nodespec,
                str2bool(kwargs.get('force'))
            )

            self._logger.debug(
                'NodeController.deleteNode(): delete request queued: %s' % (
                    transaction_id))

            response = dict(transaction_id=transaction_id)
        except (OperationFailed, NodeNotFound) as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.errorResponse(str(ex)) \
                if isinstance(ex, OperationFailed) else \
                self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:  # noqa pylint: disable=broad-except
            self._logger.exception('node WS API deleteNode() failed')
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
