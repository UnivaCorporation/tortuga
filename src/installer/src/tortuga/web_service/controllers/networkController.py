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

import cherrypy

from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.objects.network import Network
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.utility.helper import str2bool
from tortuga.web_service.auth.decorators import authentication_required
from .tortugaController import TortugaController
from .. import app


class NetworkController(TortugaController):
    """
    Admin network controller class.

    """
    actions = [
        {
            'name': 'getNetworkList',
            'path': '/v1/networks/',
            'action': 'getNetworkList',
            'method': ['GET'],
        },
        {
            'name': 'getNetwork',
            'path': '/v1/networks/:(network_id)',
            'action': 'getNetwork',
            'method': ['GET'],
        },
        {
            'name': 'addNetwork',
            'path': '/v1/networks/:(address)/:(netmask)',
            'action': 'addNetwork',
            'method': ['POST'],
        },
        {
            'name': 'deleteNetwork',
            'path': '/v1/networks/:(id)',
            'action': 'deleteNetwork',
            'method': ['DELETE'],
        },
        {
            'name': 'updateNetwork',
            'path': '/v1/networks/:(network_id)',
            'action': 'updateNetwork',
            'method': ['PUT'],
        },
    ]

    @cherrypy.tools.json_out()
    @authentication_required()
    def getNetworkList(self, **kwargs):
        """
        Return list of all available networks
        """

        try:
            if 'address' in kwargs and 'netmask' in kwargs:
                networkList = TortugaObjectList(
                    [app.network_api.getNetwork(
                        kwargs['address'], kwargs['netmask'])])
            else:
                networkList = app.network_api.getNetworkList()

            response = {'networks': networkList.getCleanDict()}
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getNetwork(self, address, netmask):
        """Return networks"""

        # self.getLogger().debug('Retrieving network %s/%s' % (
        #     address, netmask))

        try:
            network = app.network_api.getNetwork(
                address, netmask)

            response = {'network': network.getCleanDict()}
        except NetworkNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getNetworkById(self, network_id):
        """Return networks by id"""

        self.getLogger().debug('Retrieving network id [%s]' % (network_id))

        try:
            network = app.network_api.getNetworkById(network_id)

            response = {'network': network.getCleanDict()}
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def addNetwork(self, address, netmask):
        '''
        Handle put to networks/:(address)/:(netmask)/)
        '''

        response = None

        postdata = cherrypy.request.json

        network = Network.getFromDict(postdata)

        try:
            # Make sure the values are synced
            network.setAddress(address)
            network.setNetmask(netmask)

            app.network_api.addNetwork(network)
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def deleteNetwork(self, network_id):
        '''
        Handle delete to networks/:(id)
        '''

        response = None

        try:
            app.network_api.deleteNetwork(network_id)
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def __update_network(self, network, postdata): \
            # pylint: disable=no-self-use
        updated = False

        if 'address' in postdata:
            network.setAddress(network['address'])

            updated = True

        if 'gateway' in postdata:
            network.setGateway(postdata['gateway'])

            updated = True

        if 'increment' in postdata:
            network.setIncrement(postdata['increment'])

            updated = True

        if 'netmask' in postdata:
            network.setNetmask(postdata['netmask'])

            updated = True

        if 'name' in postdata:
            network.setName(postdata['name'])

            updated = True

        if 'options' in postdata:
            network.setOptions(postdata['options'])

            updated = True

        if 'suffix' in postdata:
            network.setSuffix(postdata['suffix'])

            updated = True

        if 'type' in postdata:
            network.setType(postdata['type'])

            updated = True

        if 'usingDhcp' in postdata:
            network.setUsingDhcp(str2bool(postdata['usingDhcp']))

            updated = True

        if 'startIp' in postdata:
            network.setStartIp(postdata['startIp'])

            updated = True

        return updated

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def updateNetwork(self, network_id):
        '''
        Handle put to networks/:(id)
        '''

        response = None

        try:
            if 'network' not in cherrypy.request.json:
                # Malformed request
                raise Exception('Malformed request: missing \'network\' key')

            network = app.network_api.getNetworkById(network_id)

            if self.__update_network(
                    network, cherrypy.request.json['network']):
                network.setId(network_id)

                app.network_api.updateNetwork(network)
        except NetworkNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().error('%s' % (ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
