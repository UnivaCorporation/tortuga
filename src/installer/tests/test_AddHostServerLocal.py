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

from tortuga.addhost.addHostServerLocal import (AddHostServerLocal,
                                                get_host_name)
from tortuga.db.models.node import Node
from tortuga.db.networksDbHandler import NetworksDbHandler

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


def test_get_host_name():
    assert get_host_name('host.domain') == 'host'
