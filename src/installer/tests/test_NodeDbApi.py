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

from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.exceptions.nodeNotFound import NodeNotFound


def test_getNode(dbm):
    with dbm.session() as session:
        result = NodeDbApi().getNode(session, 'compute-01.private')

    assert isinstance(result, Node)


def test_getNode_with_options(dbm):
    options = dict(hardwareprofile=True)

    with dbm.session() as session:
        result = NodeDbApi().getNode(session, 'compute-01.private', options)

    assert isinstance(result, Node)

    assert result.getHardwareProfile().getName()


def test_getNodeByAddHostSession(dbm):
    with dbm.session() as session:
        result = NodeDbApi().getNodesByAddHostSession(session, 'xxxx')

    assert not result


def test_getNodesByNameFilter(dbm):
    with dbm.session() as session:
        result = NodeDbApi().getNodesByNameFilter(session, 'compute-*')

    assert isinstance(result, TortugaObjectList)

    assert result[0].getName().startswith('compute-')


def test_getNodeById(dbm):
    with dbm.session() as session:
        result = NodeDbApi().getNodeById(session, 1)

    assert isinstance(result, Node)


def test_getNodeByIp(dbm):
    with dbm.session() as session:
        with pytest.raises(NodeNotFound):
            result = NodeDbApi().getNodeByIp(session, '127.0.0.1')


def test_getNodeList(dbm):
    with dbm.session() as session:
        result = NodeDbApi().getNodeList(session)

    assert isinstance(result, TortugaObjectList)

    assert isinstance(result[0], Node)
