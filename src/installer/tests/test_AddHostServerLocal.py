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

# pylint: disable=protected-access

import pytest

from tortuga.addhost.addHostServerLocal import (AddHostServerLocal,
                                                get_host_name)
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.models.node import Node
from tortuga.db.networksDbHandler import NetworksDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.invalidMacAddress import InvalidMacAddress


api = AddHostServerLocal()


def test_generate_node_name(dbm):
    name_format = 'compute-#NN'

    with dbm.session() as session:
        name1 = api.generate_node_name(session, name_format)

        # fixture sets up compute-01..compute-10; next generated name
        # must be 'compute-11'
        assert name1 == 'compute-11'

        name2 = api.generate_node_name(session, name_format)

        assert name1 != name2, 'failed to generate unique node name'

        api.clear_session_node(Node(name=name1))

        name3 = api.generate_node_name(session, name_format)

        assert name1 == name3


def test_generate_provisioning_ip_address(dbm):
    with dbm.session() as session:
        networks = NetworksDbHandler().getNetworkList(session)

        result = api.generate_provisioning_ip_address(networks[0])

        assert result

def test_failed_initializeNode(dbm):
    with dbm.session() as session:
        hardware_profile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'nonetwork'
        )

        software_profile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute'
        )

        node = Node()

        with pytest.raises(NetworkNotFound):
            api.initializeNode(
                session, node, hardware_profile, software_profile, [])


def test_initializeNode(dbm):
    with dbm.session() as session:
        hardware_profile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localiron'
        )

        software_profile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute'
        )

        node = Node()

        nic_defs = [
            {
                'mac': '00:00:00:00:00:01',
            }
        ]

        api.initializeNode(
            session, node, hardware_profile, software_profile, nic_defs)

        assert node.name
        assert node.nics and len(node.nics) == 1 and \
            node.nics[0].mac == '00:00:00:00:00:01' and \
            node.nics[0].boot


@pytest.mark.parametrize('mac', [
    '000000000000',
    '00:00:00:00:00:01',
    'abababababab',
    pytest.param('ab', marks=pytest.mark.xfail(raises=InvalidMacAddress)),
    pytest.param(None, marks=pytest.mark.xfail(raises=InvalidMacAddress)),
    pytest.param('', marks=pytest.mark.xfail(raises=InvalidMacAddress)),
    pytest.param('xxxxxxxxxxxx',
                 marks=pytest.mark.xfail(raises=InvalidMacAddress)),
    pytest.param('ababababababaa',
                 marks=pytest.mark.xfail(raises=InvalidMacAddress)),
    pytest.param('ab:ax:bc:ed:ee:aa',
                 marks=pytest.mark.xfail(raises=InvalidMacAddress)),
])
def test_validate_mac_address(dbm, mac):
    with dbm.session() as session:
        prov_network = NetworksDbHandler().getNetworkList(session)[0]

        api._validate_mac_address(session, mac, prov_network)


def test_get_host_name():
    assert get_host_name('host.domain') == 'host'
