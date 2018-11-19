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

from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.models.hardwareProfile import HardwareProfile


@pytest.mark.usefixtures('dbm_class')
class TestHardwareProfilesDbHandler(unittest.TestCase):
    def setUp(self):
        self.session = self.dbm.openSession()

    def tearDown(self):
        self.dbm.closeSession()
        self.session = None

    def test_getHardwareProfileList(self):
        result = HardwareProfilesDbHandler(). getHardwareProfileList(
            self.session)

        assert isinstance(result, list)

    def test_getHardwareProfileList_tags(self):
        # 'tag1' returns hardware profile 'profile1' only
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags={'tag1': None})

        assert result and len(result) == 1 and result[0].name == 'profile1'

    def test_no_matching_tags(self):
        # Ensure invalid tag returns no result
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags={'invalid': None})

        assert not result

    def test_getHardwareProfileList_tag2(self):
        # 'tag2' returns hardware profile 'profile2' only
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags={'tag2': None})

        assert result and len(result) == 1 and result[0].name == 'profile2'

    def test_getHardwareProfileList_tag1_and_tag2(self):
        # 'tag1' and 'tag2' returns both profiles
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags={'tag1': None, 'tag2': None})

        assert result and len(result) == 2 and \
            result[0].name == 'profile1' and result[1].name == 'profile2'

    def test_getHardwareProfile_resource_adapter_config(self):
        result = HardwareProfilesDbHandler().getHardwareProfile(
            self.session, 'aws2')

        assert result.default_resource_adapter_config and \
            result.default_resource_adapter_config.name != 'default'

        assert result.default_resource_adapter_config.resourceadapter == \
            result.resourceadapter

        assert result.default_resource_adapter_config.name == 'nondefault'

    def test_getHardwareProfile_resource_adapter_config_no_default(self):
        result = HardwareProfilesDbHandler().getHardwareProfile(
            self.session, 'aws'
        )

        assert result.default_resource_adapter_config is None
