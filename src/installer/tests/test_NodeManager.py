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

import mock
import pytest

from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.node.nodeManager import NodeManager
from .osUtilityMock import get_os_object_factory


@mock.patch('tortuga.os_utility.osUtility.getOsObjectFactory',
            side_effect=get_os_object_factory)
class TestNodeManager:

    def test_simple_validate_delete_nodes_request(
            self, get_os_object_factory_mock): \
            # pylint: disable=unused-argument
        """
        Simple delete of multiple nodes in same software profile
        """

        swprofile = SoftwareProfile(name='swprofile1', lockedState='Unlocked')

        nodes = [
            Node(name='compute-01', softwareprofile=swprofile),
            Node(name='compute-02', softwareprofile=swprofile),
        ]

        NodeManager()._NodeManager__validate_delete_nodes_request(nodes, False)

    def test_validate_delete_nodes_request_alt(
            self, get_os_object_factory_mock): \
            # pylint: disable=unused-argument
        """
        Simple delete of multiple nodes with one profile locked and one not
        """

        swprofile1 = SoftwareProfile(name='swprofile1', lockedState='Unlocked')
        swprofile2 = SoftwareProfile(name='swprofile1', lockedState='SoftLocked')

        nodes = [
            Node(name='compute-01', softwareprofile=swprofile1),
            Node(name='compute-02', softwareprofile=swprofile2),
        ]

        with pytest.raises(OperationFailed):
            NodeManager()._NodeManager__validate_delete_nodes_request(
                nodes, False)

    def test_simple_validate_delete_nodes_request_alt(
            self, get_os_object_factory_mock): \
            # pylint: disable=unused-argument
        """
        Delete from soft locked software profile without force
        """

        nodes = [
            Node(name='compute-01',
                softwareprofile=SoftwareProfile(name='swprofile1',
                                                lockedState='SoftLocked')),
        ]

        with pytest.raises(OperationFailed):
            NodeManager()._NodeManager__validate_delete_nodes_request(
                nodes, False)


    def test_simple_validate_delete_nodes_request_alt_with_force(
            self, get_os_object_factory_mock): \
            # pylint: disable=unused-argument
        """
        Delete from soft locked software profile with force
        """

        nodes = [
            Node(name='compute-01',
                softwareprofile=SoftwareProfile(name='swprofile1',
                                                lockedState='SoftLocked')),
        ]

        NodeManager()._NodeManager__validate_delete_nodes_request(nodes, True)


    def test_simple_validate_delete_nodes_request_alt2(
            self, get_os_object_factory_mock): \
            # pylint: disable=unused-argument
        """
        Delete from hard locked software profile
        """

        nodes = [
            Node(name='compute-01',
                softwareprofile=SoftwareProfile(name='swprofile1',
                                                lockedState='HardLocked')),
        ]

        with pytest.raises(OperationFailed):
            NodeManager()._NodeManager__validate_delete_nodes_request(
                nodes, False)
