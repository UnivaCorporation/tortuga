#!/usr/bin/env python

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
import unittest

import pytest
from tortuga.db.models.node import Node
from tortuga.db.models.tag import Tag
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound


@pytest.mark.usefixtures('dbm_class')
class TestNodesDbHandler(unittest.TestCase):
    def setUp(self):
        super(TestNodesDbHandler, self).setUp()

        self.session = self.dbm.openSession()

    def tearDown(self):
        # Perform session clean up before calling superclass
        self.dbm.closeSession()
        self.session = None

        super(TestNodesDbHandler, self).tearDown()

    def test_getNode(self):
        result = NodesDbHandler().getNode(self.session, socket.getfqdn())

        assert result.nics

    def test_getNode_failed(self):
        with pytest.raises(NodeNotFound):
            NodesDbHandler().getNode(self.session, 'XXXXXXXX')

    def test_getNodeByIp(self):
        result = NodesDbHandler().getNodeByIp(self.session, '10.2.0.1')

        assert result.name == socket.getfqdn()

        assert result.nics

    def test_getNodesByTags(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name,)])

        assert result

        assert nodes[0] in result
        assert nodes[1] in result
        assert nodes[2] in result
        assert nodes[3] in result

    def test_getNodesByTags_match_multiple(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name,), (tags[1].name,)])

        assert result

        assert nodes[0] in result
        assert nodes[1] in result
        assert nodes[2] in result
        assert nodes[3] in result

    def test_getNodesByTags_match_multiple_with_values(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name, tags[0].value),
                           (tags[1].name, tags[1].value)])

        assert result

        assert nodes[0] in result
        assert nodes[1] in result
        assert nodes[2] in result
        assert nodes[3] in result

    def test_getNodesByTags_nonexistent(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [('invalid_tag',)])

        assert not result

    def test_getNodesByTags_value_match(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name, tags[0].value)])

        assert result

        assert nodes[0] in result
        assert nodes[1] in result
        assert nodes[2] in result
        assert nodes[3] in result

    def test_getNodesByTags_value_mismatch(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name, 'invalid_value',)])

        assert not result

    def test_getNodesByTags_one_match_one_nomatch(self):
        tags = get_tags()
        nodes = get_nodes()

        populate(self.session, tags, nodes)

        result = NodesDbHandler().getNodesByTags(
            self.session, [(tags[0].name, tags[0].value),
                           ('nomatch',)])

        assert result

        assert len(result) == 4

        # Match expected tags
        assert nodes[0] in result
        assert nodes[1] in result
        assert nodes[2] in result
        assert nodes[3] in result



def get_tags():
    tag1 = Tag(name='tag1', value='value1')
    tag2 = Tag(name='tag2', value='value2')
    tag3 = Tag(name='tag3', value='value3')
    tag4 = Tag(name='tag4', value='value4')
    tag5 = Tag(name='tag5', value='value5')

    return [tag1, tag2, tag3, tag4, tag5]


def get_nodes():
    n1 = Node(name='compute-01')
    n2 = Node(name='compute-02')
    n3 = Node(name='compute-03')
    n4 = Node(name='compute-04')
    n5 = Node(name='compute-05')
    n6 = Node(name='compute-06')
    n7 = Node(name='compute-07')
    n8 = Node(name='compute-08')

    return [n1, n2, n3, n4, n5, n6, n7, n8]


def populate(session, tags, nodes):
    # 'compute-01' has all tags
    nodes[0].tags.extend(tags)

    # 'compute-02' has all tags
    nodes[1].tags.extend(tags)

    # 'compute-03' has 'tag1' and 'tag2'
    nodes[2].tags.extend([tags[0], tags[1]])

    # 'compute-04' has 'tag1' and 'tag2'
    nodes[3].tags.extend([tags[0], tags[1]])

    # 'compute-05' has 'tag2' and 'tag3'
    nodes[4].tags.extend([tags[1], tags[2]])

    # 'compute-06' has 'tag2' and 'tag3'
    nodes[5].tags.extend([tags[1], tags[2]])

    # 'compute-07' has 'tag4'
    nodes[6].tags.extend([tags[3]])

    # 'compute-08' has 'tag5'
    nodes[7].tags.extend([tags[4]])

    session.add_all(tags)

    session.add_all(nodes)


if __name__ == '__main__':
    unittest.main()
