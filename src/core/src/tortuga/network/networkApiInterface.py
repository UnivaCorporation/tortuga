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

from tortuga.exceptions.abstractMethod import AbstractMethod


class NetworkApiInterface(object):
    """
    Network API interface.
    """

    def getNetwork(self, networkAddress, networkSubnet): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get network information.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        raise AbstractMethod('getNetwork() has to be implemented in the'
                             ' concrete API class.')

    def getNetworkById(self, id_): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get network information by id.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        raise AbstractMethod('getNetworkById() has to be implemented in'
                             ' the concrete API class.')

    def getNetworkList(self): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get network list.

            Returns:
                [networks]
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod(
            'getNetworkList() has to be implemented in the concrete API'
            ' class.')

    def addNetwork(self, network): \
            # pylint: disable=no-self-use,unused-argument
        """
        Add a new network to the system.

            Returns:
                network id
            Throws:
                NetworkAlreadyExists
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod('addNetwork() has to be implemented in the'
                             ' concrete API class.')

    def deleteNetwork(self, id_): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete a network from the DB.

            Returns:
                None
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        raise AbstractMethod('deleteNetwork() has to be implemented in the'
                             ' concrete API class.')

    def updateNetwork(self, network): \
            # pylint: disable=no-self-use,unused-argument
        """
        Update a network in the DB.

            Returns:
                network
            Throws:
                UserNotAuthorized
                NetworkNotFound
                TortugaException
        """
        raise AbstractMethod('updateNetwork() has to be implemented in'
                             ' the concrete API class.')
