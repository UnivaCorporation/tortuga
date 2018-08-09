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

import ipaddress

from sqlalchemy.orm.session import Session
from tortuga.db.networkDbApi import NetworkDbApi
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.objects.network import Network
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager


class NetworkManager(TortugaObjectManager):
    """
    Class for network management.

    Usage:
        # Getting db instance.
        from tortuga.network.networkManager import NetworkManager
        networkManager = NetworkManager()
    """

    def __init__(self):
        super(NetworkManager, self).__init__()

        self._networkDbApi = NetworkDbApi()

    def getNetwork(self, session: Session, address: str, netmask: str) \
            -> Network:
        return self._networkDbApi.getNetwork(session, address, netmask)

    def getNetworkById(self, session: Session, id_) -> Network:
        return self._networkDbApi.getNetworkById(session, id_)

    def getNetworkList(self, session: Session) -> TortugaObjectList:
        return self._networkDbApi.getNetworkList(session)

    def addNetwork(self, session: Session, network: Network) -> int:
        self.__validateNetwork(network)

        return self._networkDbApi.addNetwork(session, network)

    def updateNetwork(self, session: Session, network: Network) -> Network:
        self.__validateNetwork(network)

        return self._networkDbApi.updateNetwork(session, network)

    def deleteNetwork(self, session: Session, network_id: int):
        return self._networkDbApi.deleteNetwork(session, network_id)

    def __validateNetwork(self, network: Network) -> None: \
            # pylint: disable=no-self-use
        """
        Raises:
            InvalidArgument
        """

        optionDict = {}

        if 'address' in network and not network['address']:
            raise InvalidArgument('Network address not set')

        if 'netmask' in network and not network['netmask']:
            raise InvalidArgument('Network mask not set')

        # Get all of the network options
        if network.getOptions():
            for option in network.getOptions().split(';'):
                tokens = option.split('=')
                if len(tokens) == 2:
                    key, value = tokens
                    optionDict[key] = value

        if 'startIp' in network and network['startIp']:
            # Validate that the specified start IP address is on the
            # provided subnet

            startIp = ipaddress.IPv4Address(str(network['startIp']))
        else:
            # Start IP address not provided, fill it in since it can
            # be calculated

            increment = int(network['increment']) \
                if 'increment' in network and network['increment'] else 1

            startIp = ipaddress.IPv4Address(
                str(network['address'])) + increment

        ipaddrNetwork = ipaddress.IPv4Network(
            '%s/%s' % (network['address'], network['netmask']))

        if startIp not in ipaddrNetwork:
            raise InvalidArgument(
                'Starting IP address [%s] is not on network [%s]' % (
                    startIp, ipaddrNetwork))

        network['startIp'] = str(startIp)

        # Right now just check the VLAN vid
        if 'vlan' in optionDict:
            try:
                if int(optionDict['vlan']) > 4095 or \
                        int(optionDict['vlan']) < 1:
                    raise InvalidArgument(
                        'The VLAN ID must be an integer in the range'
                        ' 1-4095')
            except ValueError:
                # Convert all exceptions to this one...
                raise InvalidArgument(
                    'The VLAN ID must be an integer in the range 1-4095')
