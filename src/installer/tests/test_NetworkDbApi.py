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

import pytest
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.db.networkDbApi import NetworkDbApi
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.network import Network
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkAlreadyExists import NetworkAlreadyExists


def test_getNetworkList(dbm):
    with dbm.session() as session:
        networks = NetworkDbApi().getNetworkList(session)

        assert networks

        assert isinstance(networks[0], Network)

        assert isinstance(networks, TortugaObjectList)

        assert NetworkDbApi().getNetwork(session,
                                         networks[0].getAddress(),
                                         networks[0].getNetmask())

        assert NetworkDbApi().getNetworkById(session, networks[0].getId())


def test_getNetwork(dbm):
    with dbm.session() as session:
        with pytest.raises(NetworkNotFound):
            NetworkDbApi().getNetwork(session, 'AAAA', 'BBBB')


def test_updateNetwork_failed(dbm):
    bogus_network = Network()

    with dbm.session() as session:
        with pytest.raises(InvalidArgument):
            NetworkDbApi().updateNetwork(session, bogus_network)


def test_add_and_delete_network(dbm):
    address = '192.168.1.0'
    netmask = '255.255.255.0'

    network = Network()
    network.setAddress(address)
    network.setNetmask(netmask)
    network.setType('provision')

    with dbm.session() as session:
        NetworkDbApi().addNetwork(session, network)

        # attempt to add the same network twice..
        with pytest.raises(NetworkAlreadyExists):
            NetworkDbApi().addNetwork(session, network)

        stored_network = NetworkDbApi().getNetwork(session, address, netmask)

        assert stored_network

        new_netmask = '255.255.0.0'

        stored_network.setNetmask(new_netmask)

        assert NetworkDbApi().updateNetwork(session, stored_network)

        updated_network = NetworkDbApi().getNetworkById(session,
                                                        stored_network.getId())

        assert updated_network.getNetmask() == new_netmask

        NetworkDbApi().deleteNetwork(session, updated_network.getId())

        # attempt to delete network already deleted
        with pytest.raises(NetworkNotFound):
            NetworkDbApi().getNetwork(session, address, new_netmask)
