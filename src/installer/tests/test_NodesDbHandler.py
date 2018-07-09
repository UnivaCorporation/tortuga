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

import unittest

import pytest

from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.config.configManager import getfqdn


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
        result = NodesDbHandler().getNode(self.session, getfqdn())

        assert result.nics

    def test_getNodeList(self):
        assert isinstance(NodesDbHandler().getNodeList(self.session), list)

    def test_getNode_failed(self):
        with pytest.raises(NodeNotFound):
            NodesDbHandler().getNode(self.session, 'XXXXXXXX')

    def test_getNodeByIp(self):
        result = NodesDbHandler().getNodeByIp(self.session, '10.2.0.1')

        assert result.name == getfqdn()

        assert result.nics

    def test_getNodesByTags(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1',)])

        assert match_all_nodes(result)

    def test_getNodesByTags_match_multiple(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1',), ('key2',)])

        assert match_all_nodes(result)

    def test_getNodesByTags_match_multiple_with_values(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1'),
                           ('tag2', 'value2')])

        assert match_all_nodes(result)

    def test_getNodesByTags_nonexistent(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('invalid_tag',)])

        assert not result

    def test_getNodesByTags_value_match(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1')])

        assert match_all_nodes(result)

    def test_getNodesByTags_value_mismatch(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'invalid_value',)])

        assert not result

    def test_getNodesByTags_one_match_one_nomatch(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1'), ('nomatch',)])

        assert match_all_nodes(result)

    def test_getNodesByTag_non_contiguous(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag5',)])

        assert not set(['compute-01.private',
                        'compute-02.private',
                        'compute-08.private']) - \
            set([node.name for node in result])

    def test_getNodesByAddHostSession(self):
        nodes = NodesDbHandler().getNodesByAddHostSession(
            self.session, '1234')

        assert nodes and isinstance(nodes, list)

    def test_getNodesByAddHostSession_failed(self):
        result = NodesDbHandler().getNodesByAddHostSession(
            self.session, 'xxxxxx')

        assert not result


@pytest.mark.parametrize('state,swprofile', [
    ('Installed', 'compute',),
    pytest.param('Provisioned', 'compute',
                 marks=pytest.mark.xfail(raises=NodeNotFound)),
    pytest.param('Installed', 'blah',
                 marks=pytest.mark.xfail(raises=NodeNotFound)),
])
def test_getNodeListByNodeStateAndSoftwareProfileName(dbm, state, swprofile):
    with dbm.session() as session:
        result = NodesDbHandler().getNodeListByNodeStateAndSoftwareProfileName(
            session, state, swprofile,
        )

        if not result:
            raise NodeNotFound(
                'No nodes in software profile [{}] in state [{}]'.format(
                    state, swprofile))

    assert result


@pytest.mark.parametrize('state', [
    'Installed',
    pytest.param('Provisioned',
                 marks=pytest.mark.xfail(raises=NodeNotFound)),
    pytest.param('Installed',
                 marks=pytest.mark.xfail(raises=NodeNotFound)),
])
def test_getNodesByNodeState(dbm, state):
    with dbm.session() as session:
        result = NodesDbHandler().getNodesByNodeState(
            session, state
        )

        if not result:
            raise NodeNotFound(
                'No nodes in state [{}]'.format(state))

    assert result


@pytest.mark.parametrize('node_id', [
    1,
    pytest.param(123, marks=pytest.mark.xfail(raises=NodeNotFound)),
    pytest.param('xxxx', marks=pytest.mark.xfail(raises=NodeNotFound)),
])
def test_getNodeById(dbm, node_id):
    with dbm.session() as session:
        NodesDbHandler().getNodeById(session, node_id)


@pytest.mark.parametrize('nodespec', [
    ['c%', 'c%'],
    'c%',
    'compute%',
    'compute%.private',
    pytest.param('not%', marks=pytest.mark.xfail(raises=NodeNotFound)),
    '%.private',
    '%%e',
    '%',
    'compute-01.private',
    ['compute-01', 'compute-02'],
    ['compute-01.private', 'compute-02.private', 'compute-1%.private'],
    pytest.param(['not', 'a', 'match'],
                 marks=pytest.mark.xfail(raises=NodeNotFound)),
])
def test_getNodesByNameFilter(dbm, nodespec):
    with dbm.session() as session:
        result = NodesDbHandler().getNodesByNameFilter(session, nodespec)
        if not result:
            raise NodeNotFound(
                'No matching nodes: nodespec=[{}]'.format(nodespec))


def test_getNodesByNameFilter_without_installer(dbm):
    installer = getfqdn()

    with dbm.session() as session:
        result = NodesDbHandler().getNodesByNameFilter(
            session, '%', include_installer=False)

        assert result and \
            isinstance(result, list) and \
            installer not in [node.name for node in result]


def test_getNodesByNameFilter_with_installer(dbm):
    installer = getfqdn()

    with dbm.session() as session:
        result = NodesDbHandler().getNodesByNameFilter(
            session, '%', include_installer=True)

        assert result and \
            isinstance(result, list) and \
            installer in [node.name for node in result]


def test_getNodesByNameFilter_default(dbm):
    installer = getfqdn()

    with dbm.session() as session:
        result = NodesDbHandler().getNodesByNameFilter(session, '%')

        assert result and \
            isinstance(result, list) and \
            installer in [node.name for node in result]


def match_all_nodes(result):
    # Match expected tags
    return not set(['compute-01.private',
                    'compute-02.private',
                    'compute-03.private',
                    'compute-04.private']) - \
        set([node.name for node in result])


def test_build_node_filterspec_all():
    result = NodesDbHandler().build_node_filterspec('*')

    assert result[0] == '%'


def test_build_node_filterspec_spec():
    result = NodesDbHandler().build_node_filterspec('compute*')

    assert result[0] == 'compute%'


def test_build_node_filterspec_spec1():
    result = NodesDbHandler().build_node_filterspec('a*,b*,c*')

    assert result[0] == 'a%' and result[1] == 'b%' and result[2] == 'c%'


def test_expand_nodespec_default(dbm):
    installer = getfqdn()

    with dbm.session() as session:
        result = NodesDbHandler().expand_nodespec(session, '*')

        # the default in 'expand_nodespec' is to include the installer
        assert result and isinstance(result, list) and \
            installer in [node.name for node in result]



if __name__ == '__main__':
    unittest.main()
