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
    result = NodeDbApi().getNode('compute-01.private')

    assert isinstance(result, Node)


def test_getNode_with_options(dbm):
    options = dict(hardwareprofile=True)

    result = NodeDbApi().getNode('compute-01.private', options)

    assert isinstance(result, Node)

    assert result.getHardwareProfile().getName()


def test_getNodeByAddHostSession(dbm):
    result = NodeDbApi().getNodesByAddHostSession('xxxx')

    assert not result


def test_getNodesByNameFilter(dbm):
    result = NodeDbApi().getNodesByNameFilter('compute-*')

    assert isinstance(result, TortugaObjectList)

    assert result[0].getName().startswith('compute-')


def test_getNodeById(dbm):
    result = NodeDbApi().getNodeById(1)

    assert isinstance(result, Node)


def test_getNodeByIp(dbm):
    with pytest.raises(NodeNotFound):
        result = NodeDbApi().getNodeByIp('127.0.0.1')


def test_getNodeList(dbm):
    result = NodeDbApi().getNodeList()

    assert isinstance(result, TortugaObjectList)

    assert isinstance(result[0], Node)
