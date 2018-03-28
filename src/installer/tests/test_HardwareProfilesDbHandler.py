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
from tortuga.db.models.tag import Tag
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.hardwareProfilesDbHandler \
    import HardwareProfilesDbHandler


@pytest.mark.usefixtures('dbm_class')
class TestHardwareProfilesDbHandler(unittest.TestCase):
    def setUp(self):
        super(TestHardwareProfilesDbHandler, self).setUp()

        self.session = self.dbm.openSession()

        self.hardwareprofiles = get_hardware_profiles()
        self.tags = get_tags()

        # 'profile1' has 'tag1'
        # 'profile2' has 'tag2'
        populate(self.session, self.hardwareprofiles, self.tags)

    def tearDown(self):
        self.dbm.closeSession()
        self.session = None

        super(TestHardwareProfilesDbHandler, self).tearDown()

    def test_getHardwareProfileList(self):
        result = HardwareProfilesDbHandler().\
            getHardwareProfileList(self.session)

        assert isinstance(result, list)

    def test_getHardwareProfileList_tags(self):
        # 'tag1' returns hardware profile 'profile1' only
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags=[(self.tags[0].name,)])

        assert result

        assert len(result) == 1

        assert self.tags[0] in result[0].tags

    def test_no_matching_tags(self):
        # Ensure invalid tag returns no result
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags=[('invalid',)])

        assert not result

    def test_getHardwareProfileList_tag2(self):
        # 'tag2' returns hardware profile 'profile2' only
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags=[(self.tags[1].name,)])

        assert result

        assert len(result) == 1

        assert self.tags[1] in result[0].tags

    def test_getHardwareProfileList_tag1_and_tag2(self):
        # 'tag1' and 'tag2' returns both profiles
        result = HardwareProfilesDbHandler().getHardwareProfileList(
            self.session, tags=[(self.tags[0].name,),
                                (self.tags[1].name,)])

        assert result

        assert len(result) == 2

        assert self.hardwareprofiles[0] in result
        assert self.hardwareprofiles[1] in result


def get_tags():
    tag1 = Tag('tag1', 'value1')
    tag2 = Tag('tag2', 'value2')

    return [tag1, tag2]


def get_hardware_profiles():
    hardwareprofile1 = HardwareProfile('profile1')
    hardwareprofile2 = HardwareProfile('profile2')

    return [hardwareprofile1, hardwareprofile2]


def populate(session, hardwareprofiles=None, tags=None):
    if hardwareprofiles:
        session.add_all(hardwareprofiles)

    if tags:
        session.add_all(tags)

        hardwareprofiles[0].tags.append(tags[0])
        hardwareprofiles[1].tags.append(tags[1])
