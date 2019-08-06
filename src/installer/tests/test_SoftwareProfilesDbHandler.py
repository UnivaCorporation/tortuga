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

from tortuga.db.models.operatingSystem import OperatingSystem
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.resourceNotFound import ResourceNotFound


@pytest.mark.usefixtures('dbm_class')
class TestSoftwareProfilesDbHandler(unittest.TestCase):
    def setUp(self):
        self.session = self.dbm.openSession()

    def tearDown(self):
        self.dbm.closeSession()
        self.session = None

    def test_getSoftwareProfileList(self):
        result = SoftwareProfilesDbHandler().\
            getSoftwareProfileList(self.session)

        assert isinstance(result, list)

    def test_getSoftwareProfileList_by_type(self):
        """
        Get software profile list by type 'installer'
        """

        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, profile_type='installer'
        )

        assert isinstance(result, list) and result and \
            isinstance(result[0], SoftwareProfile) and \
            result[0].type == 'installer'

    def test_getSoftwareProfileList_by_type2(self):
        """
        Get software profile list by type 'compute'
        """

        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, profile_type='compute'
        )

        assert isinstance(result, list) and result and \
            isinstance(result[0], SoftwareProfile) and \
            result[0].type == 'compute'

    def test_getSoftwareProfileList_tags(self):
        # 'tag1' returns software profile 'profile1' only
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags={'tag1': None})

        assert result and \
            len(result) == 1 and \
            result[0].name == 'swprofile1'

    def test_no_matching_tags(self):
        # Ensure invalid tag returns no result
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags={'invalid': None})

        assert not result

    def test_getSoftwareProfileList_tag2(self):
        # 'tag2' returns software profile 'profile2' only
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags={'tag2': None})

        assert result and \
            len(result) == 1 and \
            'tag2' in [tag.name for tag in result[0].tags]

    def test_getSoftwareProfileList_tag1_and_tag2(self):
        # 'tag1' and 'tag2' returns neither profiles (and operator)
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags={'tag1': None, 'tag2': None})

        assert len(result) == 0

    def test_get_software_profiles_with_component(self):
        result = SoftwareProfilesDbHandler().get_software_profiles_with_component(
            self.session, 'base', 'installer'
        )

        assert result and isinstance(result[0], SoftwareProfile)

        # 'installer' component must be enabled on 'Installer' software
        # profile as per the database fixture
        assert result[0].name == 'Installer'

    def test_get_software_profiles_with_component_none(self):
        result = SoftwareProfilesDbHandler().get_software_profiles_with_component(
            self.session, 'base', 'pdsh'
        )

        assert not result

    def test_get_software_profiles_with_component_variation(self):
        """
        Test with and without 'kit_version' argument expecting
        the same results.
        """

        result1 = SoftwareProfilesDbHandler().get_software_profiles_with_component(
            self.session, 'base', 'core'
        )

        assert result1

        result2 = SoftwareProfilesDbHandler().get_software_profiles_with_component(
            self.session, 'base', 'core', kit_version='7.0.3'
        )

        assert result2

        swprofile_names1 = [swprofile1.name for swprofile1 in result1]
        swprofile_names2 = [swprofile2.name for swprofile2 in result2]

        assert swprofile_names1 == swprofile_names2


    def test_get_software_profiles_with_component_failed(self):
        with pytest.raises(ResourceNotFound):
            SoftwareProfilesDbHandler().get_software_profiles_with_component(
                self.session, 'base', 'installerEXAMPLE'
            )

    def test_get_software_profiles_with_component_failed2(self):
        with pytest.raises(ResourceNotFound):
            SoftwareProfilesDbHandler().get_software_profiles_with_component(
                self.session, 'base', 'installerEXAMPLE', kit_version='1.2.3',
            )

    def test_get_software_profiles_with_component_failed2(self):
        with pytest.raises(ResourceNotFound):
            SoftwareProfilesDbHandler().get_software_profiles_with_component(
                self.session, 'baseEXAMPLE', 'installer'
            )
