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
from tortuga.db.kitsDbHandler import KitsDbHandler
from tortuga.db.models.kit import Kit
from tortuga.exceptions.kitInUse import KitInUse
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.kitAlreadyExists import KitAlreadyExists
from tortuga.objects.kit import Kit as KitTortugaObject
from tortuga.objects.component import Component as ComponentTortugaObject


def test_getKitList(dbm):
    with dbm.session() as session:
        result = KitsDbHandler().getKitList(session)

        assert isinstance(result, list)

        assert len(result)


def test_getKitList_os(dbm):
    with dbm.session() as session:
        result = KitsDbHandler().getKitList(session, os_kits_only=True)

        assert isinstance(result, list)

        assert len(result) == 1

        assert result[0].isOs


def test_getKitId(dbm):
    with dbm.session() as session:
        result = KitsDbHandler().getKitById(session, 1)

        assert isinstance(result, Kit)


@pytest.mark.parametrize('name,isOs', [
    ('base', False),
    ('centos', True),
])
def test_getKit_name_only(dbm, name, isOs):
    with dbm.session() as session:
        result = KitsDbHandler().getKit(session, name)

        assert isinstance(result, Kit)

        assert result.name == name

        assert result.isOs == isOs


def test_getKit_name_and_version(dbm):
    with dbm.session() as session:
        result = KitsDbHandler().getKit(session, 'centos', '7.4')

        assert isinstance(result, Kit)

        assert result.name == 'centos'

        assert result.isOs


def test_getKit_name_and_version_and_iteration(dbm):
    with dbm.session() as session:
        result = KitsDbHandler().getKit(session, 'centos', '7.4', '0')

        assert isinstance(result, Kit)

        assert result.name == 'centos'
        assert result.version == '7.4'
        assert result.iteration == '0'

        assert result.isOs


def test_getKit_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(KitNotFound):
            KitsDbHandler().getKit(session, 'XXXXkitXXXX')


def test_deleteKit(dbm):
    with dbm.session() as session:
        with pytest.raises(KitInUse):
            KitsDbHandler().deleteKit(
                session, 'base', version='7.0.2', iteration='0')


def test_addKit(dbm):
    with dbm.session() as session:
        name = 'testkit'
        version = '0.0.1'
        iteration = '0'

        kitObj = KitTortugaObject(name=name,
                                  version=version,
                                  iteration=iteration)

        # create dummy component
        dummy_component1 = ComponentTortugaObject(name='dummy',
                                                  version='0.0.1')

        kitObj.addComponent(dummy_component1)

        dummy_component2 = ComponentTortugaObject(name='dummy2',
                                                  version='0.0.1')

        kitObj.addComponent(dummy_component2)

        KitsDbHandler().addKit(session, kitObj)

        new_kit = KitsDbHandler().getKit(session, 'testkit')

        assert new_kit.name == 'testkit'

        assert new_kit.components

        with pytest.raises(KitAlreadyExists):
            KitsDbHandler().addKit(session, kitObj)

        KitsDbHandler().deleteKit(session, name, version, iteration)

        with pytest.raises(KitNotFound):
            KitsDbHandler().getKit(session, name)
