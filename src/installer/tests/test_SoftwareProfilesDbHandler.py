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
from tortuga.db.softwareProfiles import SoftwareProfiles
from tortuga.db.softwareProfilesDbHandler \
    import SoftwareProfilesDbHandler
from tortuga.db.operatingSystems import OperatingSystems
from tortuga.db.tags import Tags


@pytest.mark.usefixtures('dbm_class')
class TestSoftwareProfilesDbHandler(unittest.TestCase):
    def setUp(self):
        super(TestSoftwareProfilesDbHandler, self).setUp()

        self.session = self.dbm.openSession()

        self.softwareprofiles = get_software_profiles()
        self.tags = get_tags()

        # 'profile1' has 'tag1'
        # 'profile2' has 'tag2'
        populate(self.session, self.softwareprofiles, self.tags)

    def tearDown(self):
        self.dbm.closeSession()
        self.session = None

        super(TestSoftwareProfilesDbHandler, self).tearDown()

    def test_getSoftwareProfileList(self):
        result = SoftwareProfilesDbHandler().\
            getSoftwareProfileList(self.session)

        assert result

        assert len(result) == 2

        assert self.softwareprofiles[0] in result
        assert self.softwareprofiles[1] in result

    def test_getSoftwareProfileList_tags(self):
        # 'tag1' returns software profile 'profile1' only
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags=[(self.tags[0].name,)])

        assert result

        assert len(result) == 1

        assert self.tags[0] in result[0].tags

    def test_no_matching_tags(self):
        # Ensure invalid tag returns no result
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags=[('invalid',)])

        assert not result

    def test_getSoftwareProfileList_tag2(self):
        # 'tag2' returns software profile 'profile2' only
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags=[(self.tags[1].name,)])

        assert result

        assert len(result) == 1

        assert self.tags[1] in result[0].tags

    def test_getSoftwareProfileList_tag1_and_tag2(self):
        # 'tag1' and 'tag2' returns both profiles
        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            self.session, tags=[(self.tags[0].name,),
                                (self.tags[1].name,)])

        assert result

        assert len(result) == 2

        assert self.softwareprofiles[0] in result
        assert self.softwareprofiles[1] in result


def get_tags():
    tag1 = Tags('tag1', 'value1')
    tag2 = Tags('tag2', 'value2')

    return [tag1, tag2]


def get_software_profiles():
    osInfo = OperatingSystems('centos', '7', 'x86_64')

    softwareprofile1 = SoftwareProfiles('profile1')
    softwareprofile1.os = osInfo
    softwareprofile1.type = 'compute'
    softwareprofile2 = SoftwareProfiles('profile2')
    softwareprofile2.os = osInfo
    softwareprofile2.type = 'compute'

    return [softwareprofile1, softwareprofile2]


def populate(session, softwareprofiles=None, tags=None):
    if softwareprofiles:
        session.add_all(softwareprofiles)

    if tags:
        session.add_all(tags)

        softwareprofiles[0].tags.append(tags[0])
        softwareprofiles[1].tags.append(tags[1])
