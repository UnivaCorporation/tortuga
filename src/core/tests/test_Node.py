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

# pylint: disable=no-member,relative-import

import json
import pytest
from tortuga.objects.node import Node


@pytest.fixture
def node():
    tmpnode = Node('testnode')
    tmpnode.setId(1234)

    return tmpnode


def test_getFromDbDict():
    nodeDbDict = {
        'id': 1235,
        'name': 'mike',
    }

    tmpnode = Node.getFromDbDict(nodeDbDict)

    assert tmpnode.getName() == 'mike'


def test_repr(node):
    assert str(node) == 'testnode'


def test_setName(node):
    node.setName('mynode')

    assert node.getName() == 'mynode'


def test_empty_node():
    assert not Node().getName()


def test_get_from_dict():
    d = {
        'id': 9999,
        'name': 'nodename',
        'hardwareprofile': {
            'name': 'LocalIron',
        },
        'softwareprofile': {
            'name': 'Compute',
        }
    }

    tmpnode = Node.getFromDict(d)

    assert tmpnode.getId() == 9999

    assert tmpnode.getName() == 'nodename'

    assert tmpnode.getHardwareProfile().getName() == 'LocalIron'

    assert tmpnode.getSoftwareProfile().getName() == 'Compute'


def test_node_getFromJson():
    nodedict = {
        'name': 'mike',
    }

    jsonstr = json.dumps(nodedict)

    tmpnode = Node.getFromJson(jsonstr)

    assert tmpnode.getName() == 'mike'


def test_node_getFromXml():
    xmlstr = '<node name="mike"/>'

    tmpnode = Node.getFromXml(xmlstr)

    assert tmpnode.getName() == 'mike'


def test_node_getXmlRep(node):
    xmlstr = node.getXmlRep()

    tmpnode = Node.getFromXml(xmlstr)

    assert tmpnode.getName() == 'testnode'


def test_node_getCleanDict(node):
    node_dict = node.getCleanDict()

    assert 'name' in node_dict


def test_node_encode_decode(node):
    node.encode()

    assert node.getName() == 'testnode'

    node.decode()

    assert node.getName() == 'testnode'


def test_node_setBootFrom():
    with pytest.raises(ValueError):
        Node(name='mike').setBootFrom('mmmm')
