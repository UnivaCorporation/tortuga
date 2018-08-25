import socket
from unittest.mock import MagicMock, Mock, create_autospec, patch

import pytest

from tortuga.kit.installer import KitInstallerBase
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.objects.node import Node
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound


@patch('tortuga.softwareprofile.softwareProfileManager'
       '.SoftwareProfileManager.get_software_profile_metadata')
@pytest.mark.usefixtures('dbm_class')
class TestNodeApi:
    def test_getNodeList(self, get_software_profile_metadata_mock):
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
    
        assert(isinstance(result, TortugaObjectList))
    
        node = result[0]
    
        metadata = node.getSoftwareProfile().getMetadata()
    
        assert(metadata == fake_metadata)
    
        get_software_profile_metadata_mock.assert_called()

    # def test_getNode(self, get_software_profile_metadata_mock):
    #     pass

    def test_getNodeById(self, get_software_profile_metadata_mock):
        from tortuga.node.nodeApi import NodeApi

        node_id = 1
    
        with self.dbm.session() as session:
            node = NodeApi().getNodeById(session, node_id)
    
            assert(node.getId() == node_id)
    
            assert(node.getName() == socket.getfqdn())
    
        get_software_profile_metadata_mock.assert_called_with(
            session, node.getSoftwareProfile().getName())

    def test_getNodeById_nonexistent(
            self, get_software_profile_metadata_mock):
        from tortuga.node.nodeApi import NodeApi
    
        with pytest.raises(NodeNotFound):
            with self.dbm.session() as session:
                node = NodeApi().getNodeById(session, 99999)

    @patch('tortuga.resourceAdapter.resourceAdapterFactory.get_resourceadapter_class')
    @patch('tortuga.resourceAdapter.default.Default')
    @patch('tortuga.os_objects.rhel.bootHostManager.BootHostManager')
    def test_transferNode(
        self,
        get_resourceadapter_class_mock,
        default_resource_adapter_mock,
        boot_host_manager_mock,
        get_software_profile_metadata_mock
    ):
        from tortuga.node.nodeApi import NodeApi

        with patch('tortuga.node.nodeManager.KitActionsManager.refresh') as \
                kit_actions_manager_refresh_mock:
            nodeApi = NodeApi()

            with self.dbm.session() as session:
                result = nodeApi.transferNode(
                    session, 'compute-01.private', 'compute2')

                print(result)

                print(result[0]['node'].softwareprofile)

                kit_actions_manager_refresh_mock.assert_called()

                result2 = nodeApi.transferNode(session, 'compute-01.private', 'compute')

    def test_invalid_software_profile_transferNode(self, get_software_profile_metadata_mock): \
        # pytest: disable=unused-argument
        
        from tortuga.node.nodeApi import NodeApi

        with pytest.raises(SoftwareProfileNotFound):
            with self.dbm.session() as session:
                NodeApi().transferNode(session, 'compute-01.private', 'Compute2')
