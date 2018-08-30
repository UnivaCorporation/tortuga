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

import socket
from unittest.mock import patch

import pytest

from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
from tortuga.objects.tortugaObject import TortugaObjectList


@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
@patch('tortuga.softwareprofile.softwareProfileManager'
       '.SoftwareProfileManager.get_software_profile_metadata')
@pytest.mark.usefixtures('dbm_class')
class TestNodeApi:
    def test_getNodeList(self, get_software_profile_metadata_mock,
                         get_os_boot_host_manager_mock): \
            # pylint: disable=unused-argument
        """
        Get all nodes
        """

        fake_metadata = {
            'mike': {
                'tag': 'value',
            }
        }

        get_software_profile_metadata_mock.return_value = fake_metadata

        from tortuga.node.nodeApi import NodeApi

        with self.dbm.session() as session:
            result = NodeApi().getNodeList(session)

        assert isinstance(result, TortugaObjectList)

        node = result[0]

        metadata = node.getSoftwareProfile().getMetadata()

        assert metadata == fake_metadata

        get_software_profile_metadata_mock.assert_called()

    # def test_getNode(self, get_software_profile_metadata_mock):
    #     pass

    def test_getNodeById(self, get_software_profile_metadata_mock,
                         get_os_boot_host_manager_mock): \
            # pylint: disable=unused-argument
        from tortuga.node.nodeApi import NodeApi

        node_id = 1

        with self.dbm.session() as session:
            node = NodeApi().getNodeById(session, node_id)

            assert node.getId() == node_id

            # this is a bit of a cheat since it compares host names only
            # but that should be sufficient here...
            assert node.getName().split('.', 1)[0] == \
                socket.getfqdn().split('.', 1)[0]

        get_software_profile_metadata_mock.assert_called_with(
            session, node.getSoftwareProfile().getName())

    def test_getNodeById_nonexistent(
            self, get_software_profile_metadata_mock,
            get_os_boot_host_manager_mock): \
            # pylint: disable=unused-argument
        from tortuga.node.nodeApi import NodeApi

        with pytest.raises(NodeNotFound):
            with self.dbm.session() as session:
                NodeApi().getNodeById(session, 99999)

    @patch('tortuga.resourceAdapter.resourceAdapterFactory.get_resourceadapter_class')
    @patch('tortuga.resourceAdapter.default.Default')
    def test_transferNodes_single_node(
            self,
            get_resourceadapter_class_mock,
            default_resource_adapter_mock,
            # boot_host_manager_mock,
            get_software_profile_metadata_mock,
            get_os_boot_host_manager_mock
        ):  # pylint: disable=unused-argument
        from tortuga.node.nodeApi import NodeApi

        with patch('tortuga.node.nodeManager.KitActionsManager.refresh') as \
                kit_actions_manager_refresh_mock:
            nodeApi = NodeApi()

            with self.dbm.session() as session:
                nodeApi.transferNodes(
                    session, 'compute2', nodespec='compute-01.private')

                kit_actions_manager_refresh_mock.assert_called()

                nodeApi.transferNodes(
                    session, 'compute', nodespec='compute-01.private')

    def test_invalid_software_profile_transferNode(
            self, get_software_profile_metadata_mock,
            get_os_boot_host_manager_mock): \
        # pylint: disable=unused-argument

        from tortuga.node.nodeApi import NodeApi

        with pytest.raises(SoftwareProfileNotFound):
            with self.dbm.session() as session:
                NodeApi().transferNodes(
                    session, 'Compute2', nodespec='compute-01.private')
