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

from tortuga.db.networkDevicesDbHandler import NetworkDevicesDbHandler
from tortuga.exceptions.networkDeviceNotFound import NetworkDeviceNotFound


def test_createNetworkDeviceIfNotExists(dbm):
    api = NetworkDevicesDbHandler()

    device_name = 'eth0'

    with dbm.session() as session:
        # query interface known to exist
        existing_eth0 = api.get_network_device(session, device_name)

        result = api.createNetworkDeviceIfNotExists(session, device_name)

        # ensure result matches existing network device record
        assert result and \
            result.name == device_name and \
            result.id == existing_eth0.id


def test_createNetworkDeviceIfNotExists_alt(dbm):
    api = NetworkDevicesDbHandler()

    device_name = 'eth2EXAMPLE'

    with dbm.session() as session:
        result = api.createNetworkDeviceIfNotExists(session, device_name)

        assert result

        session.add(result)

        session.commit()

        result2 = api.get_network_device(session, device_name)

        assert result2 and result2.name == device_name and result.name == result2.name


def test_get_network_device(dbm):
    with dbm.session() as session:
        result = NetworkDevicesDbHandler().get_network_device(
            session, 'eth0')

        assert result


def test_get_network_device_non_existent(dbm):
    with dbm.session() as session:
        result = NetworkDevicesDbHandler().get_network_device(
            session, 'eth0EXAMPLE')

        assert not result


def test_getNetworkDevice_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(NetworkDeviceNotFound):
            NetworkDevicesDbHandler().getNetworkDevice(
                session, 'eth0EXAMPLE')


def test_getNetworkDevice(dbm):
    with dbm.session() as session:
        result = NetworkDevicesDbHandler().getNetworkDevice(
            session, 'eth0')

        assert result and result.name == 'eth0'

