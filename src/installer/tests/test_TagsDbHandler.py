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
from tortuga.db.tagsDbHandler import TagsDbHandler


@pytest.mark.usefixtures('dbm_class')
class TestTagsDbHandler(unittest.TestCase):
    def setUp(self):
        super(TestTagsDbHandler, self).setUp()

        self.session = self.dbm.openSession()

        self._tags = []
        self._populate()

    def tearDown(self):
        self.dbm.closeSession()
        self.session = None

        super(TestTagsDbHandler, self).tearDown()

    def _populate(self):
        self._tags = [
            Tag('tag1', 'value1'),
            Tag('tag2', 'value2'),
        ]

        self.session.add_all(self._tags)

    def test_get_tag(self):
        result = TagsDbHandler().get_tag(self.session, 'tag1')

        assert result

        assert result.name == 'tag1'

    def test_get_tags(self):
        result = TagsDbHandler().get_tags(self.session)

        assert result

        assert len(result) == 2

        assert self._tags[0] in result

        assert self._tags[1] in result


if __name__ == '__main__':
    unittest.main()
