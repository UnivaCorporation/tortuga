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

# pylint: disable=multiple-statements,no-member,not-callable

from typing import Optional

from sqlalchemy.exc import IntegrityError
from tortuga.db.dbManager import DbManager
from tortuga.db.networksDbHandler import NetworksDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.deleteNetworkFailed import DeleteNetworkFailed
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkAlreadyExists import NetworkAlreadyExists
from tortuga.exceptions.networkInUse import NetworkInUse
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.network import Network
from tortuga.objects.tortugaObject import TortugaObjectList

from .models.network import Network as NetworkModel


class NetworkDbApi(TortugaDbApi):
    """
    Network DB API class.
    """

    def __init__(self):
        super().__init__()

        self._networksDbHandler = NetworksDbHandler()

    def getNetworkList(self) -> TortugaObjectList:
        """
        Get list of networks from the db.
        """

        self.getLogger().debug('getNetworkList()')

        with DbManager().session() as session:
            try:
                dbList = self._networksDbHandler.getNetworkList(session)

                return self.getTortugaObjectList(Network, dbList)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNetwork(self, address: str, netmask: str):
        """
        Get a network from the db.
        """

        self.getLogger().debug(
            'Retrieving network [%s/%s]' % (address, netmask))

        with DbManager().session() as session:
            try:
                network = self._networksDbHandler.getNetwork(
                    session, address, netmask)

                return Network.getFromDbDict(network.__dict__)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNetworkById(self, id_):
        """
        Get a network by id from the db.
        """

        self.getLogger().debug('Retrieving network ID [%s]' % (id_))

        with DbManager().session() as session:
            try:
                network = self._networksDbHandler.getNetworkById(session, id_)

                return Network.getFromDbDict(network.__dict__)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def addNetwork(self, network):
        """
        Insert network into the db.

            Returns:
                networkId
            Throws:
                NetworkAlreadyExists
        """

        self.getLogger().debug('Adding network [%s]' % network)

        with DbManager().session() as session:
            try:
                try:
                    self._networksDbHandler.getNetwork(
                        session, network.getAddress(), network.getNetmask())

                    raise NetworkAlreadyExists(
                        'Network [%s] already exists' % (network))
                except NetworkNotFound:
                    pass

                dbNetwork = self.__populateNetwork(network)

                session.add(dbNetwork)

                session.commit()

                self.getLogger().info('Added network [%s]' % (network))

                return dbNetwork.id
            except TortugaException:
                session.rollback()

                raise
            except Exception as ex:
                session.rollback()

                self.getLogger().exception('%s' % ex)

                raise

    def updateNetwork(self, network: Network):
        """
        Updates network in DB..

            Returns:
                network
            Throws:
                NetworkNotFound
                InvalidArgument
        """

        with DbManager().session() as session:
            try:
                if not network.getId():
                    raise InvalidArgument(
                        'Network id not set: unable to identify network')

                self.getLogger().debug('Updating network [%s]' % (network))

                dbNetwork = self._networksDbHandler.getNetworkById(
                    session, network.getId())

                dbNetwork = self.__populateNetwork(network, dbNetwork)

                newNetwork = Network.getFromDbDict(dbNetwork.__dict__)

                session.commit()

                self.getLogger().info('Updated network [%s]' % (network))

                return newNetwork
            except TortugaException:
                session.rollback()

                raise
            except Exception as ex:
                session.rollback()

                self.getLogger().exception('%s' % ex)

                raise

    def deleteNetwork(self, id_: int):
        """
        Delete network from the db.

            Returns:
                None
            Throws:
                NetworkInUse
                NetworkNotFound
                DeleteNetworkFailed
        """

        with DbManager().session() as session:
            try:
                dbNetwork = \
                    self._networksDbHandler.getNetworkById(session, id_)

                self.getLogger().debug(
                    'Attempting to delete network [%s/%s]' % (
                        dbNetwork.address, dbNetwork.netmask))

                # Make sure this network is not associated with anything
                if dbNetwork.hardwareprofilenetworks:
                    nets = [
                        net.hardwareprofile.name
                        for net in dbNetwork.hardwareprofilenetworks
                    ]

                    raise DeleteNetworkFailed(
                        'Network enabled on hardware profile(s): [%s]' % (
                            ' '.join(nets)))

                if dbNetwork.nics:
                    raise DeleteNetworkFailed('Network has active NIC(s)')

                session.delete(dbNetwork)

                session.commit()

                self.getLogger().info(
                    'Deleted network [%s/%s]' % (
                        dbNetwork.address, dbNetwork.netmask))
            except TortugaException:
                session.rollback()

                raise
            except IntegrityError:
                raise NetworkInUse('Network is in use')
            except Exception as ex:
                session.rollback()

                self.getLogger().exception('%s' % ex)

                raise

    def __populateNetwork(self, network: Network,
                          dbNetwork: Optional[Union[NetworkModel, None]] = None):
        if not dbNetwork:
            dbNetwork = NetworkModel()

        dbNetwork.address = network.getAddress()
        dbNetwork.netmask = network.getNetmask()
        dbNetwork.suffix = network.getSuffix()
        dbNetwork.gateway = network.getGateway()
        dbNetwork.options = network.getOptions()
        dbNetwork.name = network.getName()
        dbNetwork.startIp = network.getStartIp()
        dbNetwork.type = network.getType()
        dbNetwork.increment = network.getIncrement()
        dbNetwork.usingDhcp = network.getUsingDhcp()

        return dbNetwork
