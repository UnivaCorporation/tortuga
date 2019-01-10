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
import logging

from sqlalchemy.orm.session import Session

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.logging import NETWORKS_NAMESPACE
from tortuga.network.networkManager import NetworkManager
from tortuga.objects.network import Network
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.utility.tortugaApi import TortugaApi


class NetworkApi(TortugaApi):
    """
    Network API class.
    
    """
    def __init__(self):
        super().__init__()
        
        self._logger = logging.getLogger(NETWORKS_NAMESPACE)
        
    def getNetwork(self, session: Session, networkAddress: str,
                   networkSubnet: str):
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
            return NetworkManager().getNetwork(
                session, networkAddress, networkSubnet)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getNetworkById(self, session: Session, id_: str):
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
            return NetworkManager().getNetworkById(session, id_)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getNetworkList(self, session: Session) -> TortugaObjectList:
        """
        Get network list.

            Returns:
                [networks]
            Throws:
                UserNotAuthorized
                TortugaException
        """
        try:
            return NetworkManager().getNetworkList(session)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def addNetwork(self, session: Session, network: Network) -> int:
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
            return NetworkManager().addNetwork(session, network)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def deleteNetwork(self, session: Session, id_: str):
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
            return NetworkManager().deleteNetwork(session, id_)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def updateNetwork(self, session: Session, network: Network) -> Network:
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
            return NetworkManager().updateNetwork(session, network)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)
