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

# pylint: disable=no-member

import time
from typing import Any, Dict

from sqlalchemy.orm.session import Session
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.operatingSystem import OperatingSystem
from tortuga.db.models.operatingSystemFamily import OperatingSystemFamily
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.node import state
from tortuga.objects.parameter import Parameter


def primeDb(session: Session, settings: Dict[str, Any]):
    """
    Prime database with initial data
    """

    # Create node entry for installer
    node = Node(name=settings['fqdn'])
    node.state = state.NODE_STATE_INSTALLED
    node.lockedState = 'HardLocked'
    node.lastUpdate = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    node.bootFrom = 1

    # Create Installer Software Profile
    node.softwareprofile = SoftwareProfile(
        name=settings['installer_software_profile'],
        description='Installer software profile',
        type='installer',
        minNodes=1,
        maxNodes=1,
        lockedState='HardLocked',
    )
    node.softwareprofile.os = OperatingSystem(
        name=settings['osInfo'].getName(),
        version=settings['osInfo'].getVersion(),
        arch=settings['osInfo'].getArch()
    )

    node.softwareprofile.os.family = OperatingSystemFamily(
        name=settings['osInfo'].getOsFamilyInfo().getName(),
        version=settings['osInfo'].getOsFamilyInfo().getVersion(),
        arch=settings['osInfo'].getOsFamilyInfo().getArch()
    )

    # Create Installer Hardware Profile
    node.hardwareprofile = HardwareProfile(
        name=settings['installer_hardware_profile']
    )
    node.hardwareprofile.description = 'Installer hardware profile'
    node.hardwareprofile.nameFormat = 'installer'
    node.hardwareprofile.installType = 'package'
    node.hardwareprofile.setLocation = 'local'
    node.hardwareprofile.mappedsoftwareprofiles.append(node.softwareprofile)

    session.add(node)


def init_global_parameters(session, settings):
    # Create Global Parameters
    pApi = GlobalParametersDbHandler()

    pApi.addParameter(session, Parameter('Language', settings['language']))
    pApi.addParameter(session, Parameter('Keyboard', settings['keyboard']))
    pApi.addParameter(session, Parameter('Timezone_zone', settings['timezone']))
    pApi.addParameter(session, Parameter('Timezone_utc', settings['utc']))
    pApi.addParameter(session, Parameter('DbSchemaVers', '3'))
    pApi.addParameter(session, Parameter('IntWebPort', settings['intWebPort']))
    pApi.addParameter(
        session, Parameter('IntWebServicePort', settings['intWebServicePort']))
    pApi.addParameter(session, Parameter('WebservicePort', settings['adminPort']))
    pApi.addParameter(session, Parameter('EulaAccepted', settings['eulaAccepted']))
    pApi.addParameter(session, Parameter('DNSZone', 'private'))
    pApi.addParameter(session, Parameter('depot', settings['depotpath']))
