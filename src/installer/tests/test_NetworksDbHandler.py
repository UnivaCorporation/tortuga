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
