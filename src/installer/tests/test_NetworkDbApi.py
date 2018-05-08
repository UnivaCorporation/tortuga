import pytest
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.db.networkDbApi import NetworkDbApi
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.network import Network
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkAlreadyExists import NetworkAlreadyExists


def test_getNetworkList():
    networks = NetworkDbApi().getNetworkList()

    assert networks

    assert isinstance(networks[0], Network)

    assert isinstance(networks, TortugaObjectList)

    assert NetworkDbApi().getNetwork(networks[0].getAddress(),
                                     networks[0].getNetmask())

    assert NetworkDbApi().getNetworkById(networks[0].getId())


def test_getNetwork():
    with pytest.raises(NetworkNotFound):
        NetworkDbApi().getNetwork('AAAA', 'BBBB')


def test_updateNetwork_failed():
    bogus_network = Network()

    with pytest.raises(InvalidArgument):
        NetworkDbApi().updateNetwork(bogus_network)


def test_add_and_delete_network():
    address = '192.168.1.0'
    netmask = '255.255.255.0'

    network = Network()
    network.setAddress(address)
    network.setNetmask(netmask)
    network.setType('provision')

    NetworkDbApi().addNetwork(network)

    # attempt to add the same network twice..
    with pytest.raises(NetworkAlreadyExists):
        NetworkDbApi().addNetwork(network)

    stored_network = NetworkDbApi().getNetwork(address, netmask)

    assert stored_network

    new_netmask = '255.255.0.0'

    stored_network.setNetmask(new_netmask)

    assert NetworkDbApi().updateNetwork(stored_network)

    updated_network = NetworkDbApi().getNetworkById(stored_network.getId())

    assert updated_network.getNetmask() == new_netmask

    NetworkDbApi().deleteNetwork(updated_network.getId())

    # attempt to delete network already deleted
    with pytest.raises(NetworkNotFound):
        NetworkDbApi().getNetwork(address, new_netmask)
