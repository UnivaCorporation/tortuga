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

import json

from tortuga.network.networkApiInterface import NetworkApiInterface
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.network import Network
from .tortugaWsApi import TortugaWsApi


class NetworkWsApi(TortugaWsApi, NetworkApiInterface):
    """
    Network WS API class.
    """

    def getNetwork(self, address, netmask):
        """
        Get network information.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """

        url = 'v1/networks/%s/%s' % (address, netmask)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Network.getFromDict(responseDict.get(Network.ROOT_TAG))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNetworkById(self, id_):
        """
        Get network information by id.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """

        url = 'v1/networks/%s' % (id_)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Network.getFromDict(responseDict.get(Network.ROOT_TAG))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNetworkList(self):
        """
        Get network list.

            Returns:
                [networks]
            Throws:
                UserNotAuthorized
                TortugaException
        """

        url = 'v1/networks'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Network.getListFromDict(responseDict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addNetwork(self, network):
        """
        Add a new network to the system.

            Returns:
                (none)
            Throws:
                NetworkAlreadyExists
                UserNotAuthorized
                TortugaException
        """

        url = 'v1/networks/%s/%s' % (
            network.getAddress(), network.getNetmask())

        postdata = json.dumps(network.getCleanDict())

        try:
            self.sendSessionRequest(url, method='POST', data=postdata)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteNetwork(self, network_id):
        """
        Delete a network from the DB.

            Returns:
                None
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """

        url = 'v1/networks/%s' % (network_id)

        try:
            self.sendSessionRequest(url, method='DELETE')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateNetwork(self, network):
        """
        Update a network in the DB.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """

        url = 'v1/networks/%s' % (network.getId())

        postdata = json.dumps(network.getCleanDict())

        try:
            self.sendSessionRequest(url, method='PUT', data=postdata)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
