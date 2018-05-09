import pytest
from tortuga.db.networksDbHandler import NetworksDbHandler
from tortuga.exceptions.networkNotFound import NetworkNotFound


def test_getNetworkList(dbm):
    with dbm.session() as session:
        networks = NetworksDbHandler().getNetworkList(session)

        assert networks

        network2 = NetworksDbHandler().getNetworkById(session, networks[0].id)

        assert network2

        network3 = NetworksDbHandler().getNetwork(
            session, network2.address, network2.netmask)

        assert network3

        assert network2.id == network3.id


def test_getNetworkById(dbm):
    with dbm.session() as session:
        with pytest.raises(NetworkNotFound):
            NetworksDbHandler().getNetworkById(session, 9999)
