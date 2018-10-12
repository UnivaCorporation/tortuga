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


def test_getSoftwareProfile(dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfileDbApi().getSoftwareProfile(session,
                                                              'Installer')

        assert swprofile

        assert not swprofile.getNodes()

        assert SoftwareProfileDbApi().getSoftwareProfileById(
            session, swprofile.getId())


def test_updateSoftwareProfileTags(dbm):
    api = SoftwareProfileDbApi()
    tags = {'tag1': 'tag1 value', 'tag2': 'tag2 value'}

    with dbm.session() as session:
        swprofile = api.getSoftwareProfile(session, 'notags')

        #
        # Set tags
        #
        swprofile.setTags({'tag1': 'tag1 value', 'tag2': 'tag2 value'})
        api.updateSoftwareProfile(session, swprofile)
        session.commit()
        swprofile = api.getSoftwareProfile(session, 'notags')
        assert swprofile.getTags() == tags

        #
        # Remove tags
        #
        swprofile.setTags({})
        api.updateSoftwareProfile(session, swprofile)
        session.commit()
        swprofile = api.getSoftwareProfile(session, 'notags')
        assert swprofile.getTags() == {}


def test_getSoftwareProfile_with_options(dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfileDbApi().getSoftwareProfile(
            session, 'Installer', optionDict={'nodes': True})

    assert swprofile

    assert swprofile.getNodes()


def test_getSoftwareProfileById_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(SoftwareProfileNotFound):
            SoftwareProfileDbApi().getSoftwareProfileById(session, 9999)


def test_getSoftwareProfileList(dbm):
    with dbm.session() as session:
        assert SoftwareProfileDbApi().getSoftwareProfileList(session)


def test_getIdleSoftwareProfileList(dbm):
    with dbm.session() as session:
        assert isinstance(
            SoftwareProfileDbApi().getIdleSoftwareProfileList(session),
            TortugaObjectList)


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


def test_getAllEnabledComponentList(dbm):
    with dbm.session() as session:
        assert SoftwareProfileDbApi().getAllEnabledComponentList(session)


def test_getEnabledComponentList(dbm):
    with dbm.session() as session:
        components = SoftwareProfileDbApi().getEnabledComponentList(session,
                                                                    'Installer')

    assert components

    assert isinstance(components, TortugaObjectList)

    assert isinstance(components[0], Component)


def test_getNodeList(dbm):
    with dbm.session() as session:
        nodes = SoftwareProfileDbApi().getNodeList(session, 'Installer')

    assert isinstance(nodes, TortugaObjectList)

    assert isinstance(nodes[0], Node)

    assert nodes[0].getSoftwareProfile() is None


def test_getUsableNodes(dbm):
    with dbm.session() as session:
        nodes = SoftwareProfileDbApi().getUsableNodes(session, 'Installer')

    assert nodes


def test_copySoftwareProfile(dbm):
    with dbm.session() as session:
        SoftwareProfileDbApi().copySoftwareProfile(
            session, 'Installer', 'NotInstaller')

        assert SoftwareProfileDbApi().getSoftwareProfile(session,
                                                         'NotInstaller')

        SoftwareProfileDbApi().deleteSoftwareProfile(session,
                                                     'NotInstaller')

        with pytest.raises(SoftwareProfileNotFound):
            SoftwareProfileDbApi().getSoftwareProfile(session, 'NotInstaller')
