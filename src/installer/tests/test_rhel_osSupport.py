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

"""
WIP: needs complete unit tests implemented
"""

import pytest

from tortuga.db.models.node import Node
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.objects.osFamilyInfo import OsFamilyInfo
from tortuga.os.rhel.osSupport import OSSupport


@pytest.mark.usefixtures('dbm_class')
class TestRhelOSSupport:
    def test_getPXEReinstallSnippet(self):
        osFamilyInfo = OsFamilyInfo('rhel', '7', 'x86_64')

        osSupport = OSSupport(osFamilyInfo)

        with self.dbm.session() as session:
            node = NodesDbHandler().getNode(session, 'compute-01.private')

            ks_url = 'http://ksurl'

            result = osSupport.getPXEReinstallSnippet(ks_url, node)

            assert result and ks_url in result

    def test_validateNode(self):
        osFamilyInfo = OsFamilyInfo('rhel', '7', 'x86_64')

        osSupport = OSSupport(osFamilyInfo)

        node = Node()

        with pytest.raises(NodeNotFound):
            osSupport._OSSupport__validate_node(node)
