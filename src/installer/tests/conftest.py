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

import socket

import pytest
from sqlalchemy import create_engine

from tortuga.config.configManager import ConfigManager
from tortuga.db import (adminDbApi, globalParameterDbApi, hardwareProfileDbApi,
                        kitDbApi, networkDbApi, nodeDbApi,
                        softwareProfileDbApi)
from tortuga.db.dbManager import DbManagerBase
from tortuga.db.models.admin import Admin
from tortuga.db.models.component import Component
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.kit import Kit
from tortuga.db.models.network import Network
from tortuga.db.models.networkDevice import NetworkDevice
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.operatingSystem import OperatingSystem
from tortuga.db.models.operatingSystemFamily import OperatingSystemFamily
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.deployer.dbUtility import init_global_parameters, primeDb
from tortuga.node import nodeManager
from tortuga.objects import osFamilyInfo, osInfo


@pytest.fixture(autouse=True)
def disable_DbManager(monkeypatch, dbm):
    def mockreturn():
        return dbm

    # Patch "DbManager" in all *DbApi modules to use fixture
    monkeypatch.setattr(adminDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(globalParameterDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(hardwareProfileDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(nodeDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(softwareProfileDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(networkDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(kitDbApi, 'DbManager', mockreturn)
    monkeypatch.setattr(nodeManager, 'DbManager', mockreturn)


@pytest.fixture(scope='session')
def cm():
    return ConfigManager()


@pytest.fixture(scope='class')
def cm_class(request, cm):
    request.cls.cm = cm


@pytest.fixture(scope='session')
def dbm():
    dbm = DbManagerBase(create_engine('sqlite:///:memory:', echo=False))

    dbm.init_database()

    os_info = osInfo.OsInfo('centos', '7.4', 'x86_64')
    os_info.setOsFamilyInfo(osFamilyInfo.OsFamilyInfo('rhel', '7', 'x86_64'))

    settings = {
        'language': 'en',
        'keyboard': 'en_US',
        'timezone': 'UTC',
        'utc': 'true',
        'intWebPort': '8008',
        'intWebServicePort': '8444',
        'adminPort': '8443',
        'eulaAccepted': 'true',
        'depotpath': '/depot',
    }

    installer_fqdn = socket.getfqdn()

    with dbm.session() as session:
        primeDb(session, installer_fqdn, os_info, settings)

        init_global_parameters(session, settings)

        installer_node = session.query(Node).filter(
            Node.name == installer_fqdn).one()

        os_ = session.query(OperatingSystem).filter(
            OperatingSystem.name == 'centos').one()

        os_family = session.query(OperatingSystemFamily).filter(
            OperatingSystemFamily.name == 'rhel').one()

        admin = Admin(username='admin',
                      password='password',
                      realname='realname',
                      description='description')

        session.add(admin)

        eth1_network_device = NetworkDevice(name='eth1')

        # Add dummy provisioning network
        network = Network()
        network.address = '10.2.0.0'
        network.netmask = '255.255.255.0'
        network.name = 'Provisioning network on eth1'
        network.type = 'provision'

        session.add(network)

        installer_nic = Nic()
        installer_nic.network = network
        installer_nic.networkdevice = eth1_network_device

        installer_node.nics = [installer_nic]

        kit = Kit()
        kit.name = 'base'
        kit.version = '6.3.0'
        kit.iteration = '0'
        kit.description = 'Sample base kit'

        installer_component = Component()
        installer_component.name = 'installer'
        installer_component.version = '6.3'
        installer_component.family = [os_family]
        installer_component.kit = kit

        core_component = Component(name='core',
                                   version='6.3',
                                   description='Compute component')
        core_component.family = [os_family]
        core_component.kit = kit

        session.add(kit)

        # create OS kit
        os_kit = Kit(name='centos', version='7.4', iteration='0')
        os_kit.isOs = True
        os_component = Component(name='centos-7.4-x86_64', version='7.4')
        os_component.os = [os_]
        os_component.kit = os_kit
        os_kit.components.append(os_component)

        session.add(os_kit)

        compute_swprofile = SoftwareProfile(name='compute')
        compute_swprofile.os = os_
        compute_swprofile.components = [core_component]
        compute_swprofile.type = 'compute'

        localiron_hwprofile = HardwareProfile(name='localiron')

        for n in range(1, 11):
            compute_node = Node('compute-{0:02d}.private'.format(n))
            compute_node.softwareprofile = compute_swprofile
            compute_node.hardwareprofile = localiron_hwprofile

            session.add(compute_node)

        session.commit()

    return dbm


@pytest.fixture(scope='class')
def dbm_class(request, dbm):
    request.cls.dbm = dbm
