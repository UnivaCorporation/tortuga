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

# pylint: disable=not-callable,multiple-statements,no-member,no-self-use

from typing import Optional, Union

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.deleteNetworkFailed import DeleteNetworkFailed
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkAlreadyExists import NetworkAlreadyExists
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.objects.network import Network as NetworkObj

from .models.network import Network


class NetworksDbHandler(TortugaDbObjectHandler):
    """
    This class handles networks table.
    """

    def getNetwork(self, session: Session, address: str, netmask: str):
        """
        Return network.

        Raises:
            NetworkNotFound
        """

        self.getLogger().debug(
            'Retrieving network [%s/%s]' % (address, netmask))

        try:
            return session.query(Network).filter(
                and_(Network.address == address,
                     Network.netmask == netmask)).one()
        except NoResultFound:
            raise NetworkNotFound(
                'Network [%s/%s] not found.' % (address, netmask))

    def getNetworkById(self, session: Session, _id: int):
        """
        Return network.

        Raises:
            NetworkNotFound
        """

        if not _id:
            raise InvalidArgument('Network ID cannot be None')

        self.getLogger().debug('Retrieving network ID [%s]' % (_id))

        dbNetwork = session.query(Network).get(_id)

        if not dbNetwork:
            raise NetworkNotFound('Network ID [%s] not found.' % (_id))

        return dbNetwork

    def getNetworkList(self, session: Session,
                       network_type: Optional[Union[str, None]] = None):
        """
        Get list of networks from the db.
        """

        if network_type:
            return session.query(Network).filter(
                Network.type == network_type).all()

        self.getLogger().debug('getNetworkList()')

        return session.query(Network).all()

    def getNetworkListByType(self, session: Session, network_type: str):
        """
        Get all networks that are of type type.
        """

        self.getLogger().debug(
            'getNetworkListByType(type=%s)' % (network_type))

        return self.getNetworkList(session, network_type=network_type)

    def addNetwork(self, session: Session, network: NetworkObj):
        """
        Insert network into the db.

        Raises:
            NetworkAlreadyExists
        """

        self.getLogger().debug('Adding network [%s]' % network)

        try:
            self.getNetwork(
                session, network.getAddress(), network.getNetmask())

            raise NetworkAlreadyExists(
                'Network [%s] already exists' % (network))
        except NetworkNotFound:
            # OK.
            pass

        dbNetwork = self.__populateNetwork(network)

        session.add(dbNetwork)

        self.getLogger().info('Added network [%s]' % (network))

        return dbNetwork

    def updateNetwork(self, session: Session, network: NetworkObj):
        """
        Update network in DB.
        """

        if not network.getId():
            raise InvalidArgument(
                'Network id not set: unable to identify network')

        self.getLogger().debug('Updating network [%s]' % (network))

        dbNetwork = self.getNetworkById(session, network.getId())

        dbNetwork = self.__populateNetwork(network, dbNetwork)

        self.getLogger().info('Updated network [%s]' % (network))

        return dbNetwork

    def __populateNetwork(self, network: NetworkObj,
                          dbNetwork: Optional[Union[Network, None]] = None):
        if not dbNetwork:
            dbNetwork = Network()

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

    def deleteNetwork(self, session: Session, _id: int):
        """
        Delete network from the db.

        Raises:
            NetworkNotFound
            DeleteNetworkFailed
        """

        dbNetwork = self.getNetworkById(session, _id)

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

        self.getLogger().info(
            'Deleted network [%s/%s]' % (
                dbNetwork.address, dbNetwork.netmask))
