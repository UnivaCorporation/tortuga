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

from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.operatingSystem import OperatingSystem
from tortuga.db.models.operatingSystemFamily import OperatingSystemFamily
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.objects.parameter import Parameter


def primeDb(session, installer_fqdn, osInfo, settings):
    """
    Prime database with initial data
    """

    # Create Installer Software Profile
    swProfileName = 'Installer'

    dbSoftwareProfile = SoftwareProfile(name=swProfileName)
    dbSoftwareProfile.description = 'Installer software profile'
    dbSoftwareProfile.type = 'installer'

    dbOs = OperatingSystem()
    dbOs.name = osInfo.getName()
    dbOs.version = osInfo.getVersion()
    dbOs.arch = osInfo.getArch()

    session.add(dbOs)

    dbOsFamily = OperatingSystemFamily()
    dbOsFamily.name = osInfo.getOsFamilyInfo().getName()
    dbOsFamily.version = osInfo.getOsFamilyInfo().getVersion()
    dbOsFamily.arch = osInfo.getOsFamilyInfo().getArch()

    session.add(dbOsFamily)

    dbOs.family = dbOsFamily

    dbSoftwareProfile.os = dbOs

    session.add(dbSoftwareProfile)

    # Create Installer Hardware Profile
    hwProfileName = 'Installer'

    dbHardwareProfile = HardwareProfile(name=hwProfileName)
    dbHardwareProfile.description = 'Installer hardware profile'
    dbHardwareProfile.nameFormat = 'installer'
    dbHardwareProfile.installType = 'package'
    dbHardwareProfile.setLocation = 'local'
    dbHardwareProfile.mappedsoftwareprofiles.append(dbSoftwareProfile)

    session.add(dbHardwareProfile)

    # Create node entry for installer
    dbNode = Node(name=installer_fqdn)
    dbNode.softwareprofile = dbSoftwareProfile
    dbNode.hardwareprofile = dbHardwareProfile
    dbNode.state = 'Installed'
    dbNode.lockedState = 'HardLocked'
    dbNode.lastUpdate = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    dbNode.bootFrom = 1
    dbNode.isIdle = False

    session.add(dbNode)


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
