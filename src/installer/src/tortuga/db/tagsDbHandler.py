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

from sqlalchemy import and_

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler

from .models.tag import Tag


class TagsDbHandler(TortugaDbObjectHandler):
    def get_tags(self, session): \
            # pylint: disable=no-self-use
        return session.query(Tag).all()

    def get_tag(self, session, name, value=None): \
            # pylint: disable=no-self-use
        if value is None:
            return session.query(Tag).filter(Tag.name == name).first()

        return session.query(Tag).filter(
            and_(Tag.name == name, Tag.value == value)).first()

    def delete(self, session, name):
        tag = self.get_tag(session, name)
        if tag is None:
            return

        session.delete(tag)
