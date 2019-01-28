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

from typing import List, Optional

from sqlalchemy.orm.session import Session
from tortuga.db.models.instanceMetadata import InstanceMetadata
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler


class InstanceMetadataDbHandler(TortugaDbObjectHandler):
    """APIs for retrieving metadata"""

    def list(self, session: Session, *, filter_key: Optional[str] = None,
             filter_value: Optional[str] = None) -> List[InstanceMetadata]:
        """Return list of all metadata."""

        return filter_instance_metadata(
            session, filter_key, filter_value
        ).all()

    def delete(self, session: Session, *, filter_key: Optional[str] = None,
               filter_value: Optional[str] = None) -> None:
        """Delete metadata based on query"""
        filter_instance_metadata(
            session, filter_key, filter_value
        ).delete()


def filter_instance_metadata(session: Session, filter_key, filter_value):
    q = session.query(InstanceMetadata)

    if filter_key is not None:
        # filter on key
        q = q.filter(InstanceMetadata.key==filter_key)  # noqa

    if filter_value is not None:
        # filter on value
        q = q.filter(InstanceMetadata.value==filter_value)  # noqa

    return q
