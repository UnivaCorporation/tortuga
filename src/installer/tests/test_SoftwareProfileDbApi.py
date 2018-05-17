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

from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
# from tortuga.exceptions.updateSoftwareProfileFailed import \
#     UpdateSoftwareProfileFailed
from tortuga.objects.component import Component
from tortuga.objects.node import Node
# from tortuga.objects.osInfo import OsInfo
# from tortuga.objects.osFamilyInfo import OsFamilyInfo
# from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.objects.tortugaObject import TortugaObjectList


def test_getSoftwareProfile():
    swprofile = SoftwareProfileDbApi().getSoftwareProfile('Installer')

    assert swprofile

    assert not swprofile.getNodes()

    assert SoftwareProfileDbApi().getSoftwareProfileById(swprofile.getId())


def test_getSoftwareProfile_with_options():
    swprofile = SoftwareProfileDbApi().getSoftwareProfile(
        'Installer', optionDict={'nodes': True})

    assert swprofile

    assert swprofile.getNodes()


def test_getSoftwareProfileById_failed():
    with pytest.raises(SoftwareProfileNotFound):
        SoftwareProfileDbApi().getSoftwareProfileById(9999)


def test_getSoftwareProfileList():
    assert SoftwareProfileDbApi().getSoftwareProfileList()


def test_getIdleSoftwareProfileList():
    assert isinstance(SoftwareProfileDbApi().getIdleSoftwareProfileList(), TortugaObjectList)


# def test_addSoftwareProfile():
#     name = 'testprofile'

#     try:
#         swprofile = SoftwareProfile(name=name)

#         with pytest.raises(UpdateSoftwareProfileFailed):
#             SoftwareProfileDbApi().addSoftwareProfile(swprofile)

#         swprofile.setType('compute')

#         with pytest.raises(UpdateSoftwareProfileFailed):
#             SoftwareProfileDbApi().addSoftwareProfile(swprofile)

#         swprofile.setOsInfo(OsInfo('centos', '7', 'x86_64'))

#         swprofile.getOsInfo().setOsFamilyInfo(OsFamilyInfo('rhel', '7', 'x86_64'))

#         SoftwareProfileDbApi().addSoftwareProfile(swprofile)

#         new_swprofile = SoftwareProfileDbApi().getSoftwareProfile(name)

#         assert new_swprofile.getName() == name

#         assert new_swprofile.getType() == 'compute'

#         os_info = new_swprofile.getOsInfo()

#         assert os_info.getName() == 'centos' and \
#             os_info.getVersion() == '7' and \
#             os_info.getArch() == 'x86_64', 'Mismatched OsInfo'

#         SoftwareProfileDbApi().deleteSoftwareProfile(name)

#         with pytest.raises(SoftwareProfileNotFound):
#             SoftwareProfileDbApi().getSoftwareProfile(name)
#     finally:
#         try:
#             SoftwareProfileDbApi().deleteSoftwareProfile(name)
#         except SoftwareProfileNotFound:
#             # ignore this
#             pass


def test_getAllEnabledComponentList():
    assert SoftwareProfileDbApi().getAllEnabledComponentList()


def test_getEnabledComponentList():
    components = SoftwareProfileDbApi().getEnabledComponentList('Installer')

    assert components

    assert isinstance(components, TortugaObjectList)

    assert isinstance(components[0], Component)


def test_getNodeList():
    nodes = SoftwareProfileDbApi().getNodeList('Installer')

    assert isinstance(nodes, TortugaObjectList)

    assert isinstance(nodes[0], Node)

    assert nodes[0].getSoftwareProfile() is None


def test_getUsableNodes():
    nodes = SoftwareProfileDbApi().getUsableNodes('Installer')

    assert nodes


def test_copySoftwareProfile():
    SoftwareProfileDbApi().copySoftwareProfile('Installer', 'NotInstaller')

    assert SoftwareProfileDbApi().getSoftwareProfile('NotInstaller')

    SoftwareProfileDbApi().deleteSoftwareProfile('NotInstaller')

    with pytest.raises(SoftwareProfileNotFound):
        SoftwareProfileDbApi().getSoftwareProfile('NotInstaller')
