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

from tortuga.db.nodes import Nodes
from tortuga.db.nics import Nics
from tortuga.db.networks import Networks
from tortuga.db.hardwareProfiles import HardwareProfiles
from tortuga.db.hardwareProfileNetworks import HardwareProfileNetworks
from tortuga.resourceAdapter.utility import get_provisioning_nics, \
    get_provisioning_nic, get_provisioning_hwprofilenetwork, \
    get_hwprofile_provisioning_nic, iter_provisioning_nics, \
    NetworkNotFound, NicNotFound
import pytest


def get_network():
    network = Networks()
    network.address = '192.168.0.0'
    network.netmask = '255.255.255.0'
    network.type = 'provision'

    return network


def get_hardwareprofile():
    hwprofile = HardwareProfiles()

    hwprofile.nics = [Nics(ip='192.168.0.1', boot=True)]

    hwprofile.hardwareprofilenetworks = []

    return hwprofile


@pytest.fixture
def hardwareprofile():
    hwprofile = get_hardwareprofile()

    hwprofilenetwork = HardwareProfileNetworks()
    hwprofilenetwork.network = get_network()
    hwprofilenetwork.hardwareprofile = hwprofile

    hwprofile.hardwareprofilenetworks = [hwprofilenetwork]

    return hwprofile


@pytest.fixture
def hardwareprofile_no_networks():
    return get_hardwareprofile()


def get_nics(network):
    nic = Nics(ip='192.168.0.4', boot=True)
    nic.network = network

    nic2 = Nics(boot=False)

    return [nic, nic2]


@pytest.fixture
def nics():
    return get_nics(get_network())


def get_node():
    node = Nodes(name='compute-01.private')
    node.nics = []

    return node


@pytest.fixture
def node():
    """Return a bare Nodes object"""
    return get_node()


@pytest.fixture
def node_with_nics():
    """Return Nodes object with Nics defined"""
    network = get_network()

    node = get_node()
    node.nics = get_nics(network=network)

    return node


def test_get_provisioning_nics(node_with_nics):
    prov_nics = get_provisioning_nics(node_with_nics)

    assert prov_nics

    assert prov_nics[0].ip == '192.168.0.4'
    assert prov_nics[0].network.address == '192.168.0.0'


def test_get_provisioning_nic(node_with_nics):
    nic = get_provisioning_nic(node_with_nics)

    assert nic

    assert nic.ip == '192.168.0.4'


def test_get_provisioning_nic_no_prov_nic(node):
    with pytest.raises(NicNotFound):
        get_provisioning_nic(node)


def test_get_provisioning_hwprofilenetwork(hardwareprofile):
    hwprofilenetwork = get_provisioning_hwprofilenetwork(hardwareprofile)

    assert isinstance(hwprofilenetwork.network, Networks)


def test_get_provisioning_hwprofilenetwork_no_networks(
        hardwareprofile_no_networks):
    with pytest.raises(NetworkNotFound):
        get_provisioning_hwprofilenetwork(hardwareprofile_no_networks)


def test_get_hwprofile_provisioning_nic(hardwareprofile):
    nic = get_hwprofile_provisioning_nic(hardwareprofile)

    assert isinstance(nic, Nics)


def test_get_hwprofile_provisioning_nic_no_networks(hardwareprofile_no_networks):
    with pytest.raises(NetworkNotFound):
        get_hwprofile_provisioning_nic(hardwareprofile_no_networks)


def test_iter_provisioning_nics(nics):
    result = [nic for nic in iter_provisioning_nics(nics)]

    assert result

    assert isinstance(result[0], Nics)


def test_iter_provisioning_nics_no_nics(node):
    result = [nic for nic in iter_provisioning_nics(node.nics)]

    assert not result
