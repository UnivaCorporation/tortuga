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

from unittest.mock import patch

import pytest

from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.nodeAlreadyExists import NodeAlreadyExists
from tortuga.resourceAdapter.default import Default


@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_without_software_profile(os_obj_factory_mock):
    adapter = Default()

    with pytest.raises(CommandFailed):
        adapter.validate_start_arguments({}, None, None)


@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_validate_start_arguments(os_obj_factory_mock, dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute')
        hwprofile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localiron')

        adapter = Default()
        adapter.session = session

        addNodesRequest = {}

        # all 'default' nodes must have a 'nodeDetails' attribute in
        # addNodesRequest
        with pytest.raises(CommandFailed):
            adapter.validate_start_arguments(
                addNodesRequest, hwprofile, swprofile)


@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_empty_nodeDetails(os_obj_factory_mock, dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute')
        hwprofile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localiron')

        adapter = Default()
        adapter.session = session

        addNodesRequest = {
            'nodeDetails': [],
        }

        # all 'default' nodes must have a valid 'nodeDetails' attribute in
        # addNodesRequest

        with pytest.raises(CommandFailed):
            adapter.validate_start_arguments(
                addNodesRequest, hwprofile, swprofile)


@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_duplicate_host_name(os_obj_factory_mock, dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute')
        hwprofile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localiron')

        adapter = Default()
        adapter.session = session

        addNodesRequest = {
            'nodeDetails': [
                {
                    'name': 'compute-01.private',
                }
            ],
        }

        with pytest.raises(NodeAlreadyExists):
            adapter.validate_start_arguments(
                addNodesRequest, hwprofile, swprofile)

@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_invalid_host_name_request(os_obj_factory_mock, dbm):
    """
    CommandFailed exception should be raised if attempting to add node to
    hardware profile with name format set to "*" and without specifying a
    host name.
    """

    with dbm.session() as session:
        swprofile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute')
        hwprofile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localironalt')

        adapter = Default()
        adapter.session = session

        with pytest.raises(CommandFailed):
            adapter.validate_start_arguments({}, hwprofile, swprofile)

@patch('tortuga.node.nodeManager.osUtility.getOsObjectFactory')
def test_valid_host_name_request(os_obj_factory_mock, dbm):
    with dbm.session() as session:
        swprofile = SoftwareProfilesDbHandler().getSoftwareProfile(
            session, 'compute')
        hwprofile = HardwareProfilesDbHandler().getHardwareProfile(
            session, 'localironalt')

        adapter = Default()
        adapter.session = session

        addNodesRequest = {
            'nodeDetails': [
                {
                    'name': 'myfakename',
                    'nics': [
                        {
                        'mac': '00:00:00:00:00:01',
                        },
                    ]
                }
            ]
        }

        adapter.validate_start_arguments(addNodesRequest, hwprofile, swprofile)
