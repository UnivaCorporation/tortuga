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

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.network.networkManager import NetworkManager
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.utility.tortugaApi import TortugaApi


class NetworkApi(TortugaApi):
    """
    Network API class.
    """

    def getNetwork(self, networkAddress, networkSubnet):
        """
        Get network information.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        try:
            return NetworkManager().\
                getNetwork(networkAddress, networkSubnet)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            return NetworkManager().getNetworkById(id_)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getNetworkList(self) -> TortugaObjectList:
        """
        Get network list.

            Returns:
                [networks]
            Throws:
                UserNotAuthorized
                TortugaException
        """
        try:
            return NetworkManager().getNetworkList()
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def addNetwork(self, network):
        """
        Add a new network to the system.

            Returns:
                new network id
            Throws:
                NetworkAlreadyExists
                UserNotAuthorized
                TortugaException
        """
        try:
            return NetworkManager().addNetwork(network)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteNetwork(self, id_):
        """
        Delete a network from the DB.

            Returns:
                None
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        try:
            return NetworkManager().deleteNetwork(id_)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            return NetworkManager().updateNetwork(network)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)
