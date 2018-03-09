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
import socket
from sqlalchemy import create_engine
import sqlalchemy.orm
from tortuga.db.dbManager import DbManagerBase
from tortuga.config.configManager import ConfigManager
from tortuga.db import globalParameterDbApi, hardwareProfileDbApi, nodeDbApi, \
    softwareProfileDbApi, networkDbApi, kitDbApi, adminDbApi
from tortuga.deployer.dbUtility import primeDb, init_global_parameters
from tortuga.objects import osInfo, osFamilyInfo
from tortuga.db.admins import Admins
from tortuga.db.networks import Networks
from tortuga.db.kits import Kits
from tortuga.db.components import Components
from tortuga.db.operatingSystems import OperatingSystems
from tortuga.db.operatingSystemsFamilies import OperatingSystemsFamilies
from tortuga.db.softwareProfiles import SoftwareProfiles
from tortuga.db.nodes import Nodes
from tortuga.db.hardwareProfiles import HardwareProfiles
from tortuga.db.nics import Nics
from tortuga.db.networkDevices import NetworkDevices
from tortuga.node import nodeManager


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

        installer_node = session.query(Nodes).filter(
            Nodes.name == installer_fqdn).one()

        os_ = session.query(OperatingSystems).filter(
            OperatingSystems.name == 'centos').one()

        os_family = session.query(OperatingSystemsFamilies).filter(
            OperatingSystemsFamilies.name == 'rhel').one()

        admin = Admins('admin', 'password', 'realname', 'description')
        session.add(admin)

        eth1_network_device = NetworkDevices(name='eth1')

        # Add dummy provisioning network
        network = Networks()
        network.address = '10.2.0.0'
        network.netmask = '255.255.255.0'
        network.name = 'Provisioning network on eth1'
        network.type = 'provision'

        session.add(network)

        installer_nic = Nics()
        installer_nic.network = network
        installer_nic.networkdevice = eth1_network_device

        installer_node.nics = [installer_nic]

        kit = Kits()
        kit.name = 'base'
        kit.version = '6.3.0'
        kit.iteration = '0'
        kit.description = 'Sample base kit'

        installer_component = Components()
        installer_component.name = 'installer'
        installer_component.version = '6.3'
        installer_component.family = [os_family]
        installer_component.kit = kit

        core_component = Components(name='core',
                                    version='6.3',
                                    description='Compute component')
        core_component.family = [os_family]
        core_component.kit = kit

        compute_swprofile = SoftwareProfiles(name='compute')
        compute_swprofile.os = os_
        compute_swprofile.components = [core_component]
        compute_swprofile.type = 'compute'

        localiron_hwprofile = HardwareProfiles(name='localiron')

        session.add(kit)

        for n in range(1, 11):
            compute_node = Nodes('compute-{0:02d}.private'.format(n))
            compute_node.softwareprofile = compute_swprofile
            compute_node.hardwareprofile = localiron_hwprofile

            session.add(compute_node)

        session.commit()

    return dbm


@pytest.fixture(scope='class')
def dbm_class(request, dbm):
    request.cls.dbm = dbm
