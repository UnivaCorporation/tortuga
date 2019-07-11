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
import logging
from typing import Dict, Iterator, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, sessionmaker

from tortuga.db.dbManager import DbManager
from tortuga.db.models.hardwareProfile import HardwareProfile as DbHardwareProfile
from tortuga.db.models.hardwareProfileTag import HardwareProfileTag
from tortuga.events.types.hardware_profile import HardwareProfileTagsChanged
from tortuga.objectstore.base import matches_filters
from tortuga.typestore.base import TypeStore
from .types import HardwareProfile


logger = logging.getLogger(__name__)


class SqlalchemySessionHardwareProfileStore(TypeStore):
    """
    An implementation of the TypeStore class for HardwareProfile objects, backed
    by an Sqlalchemy database session.

    """
    type_class = HardwareProfile

    def __init__(self, db_manager: DbManager):
        self._Session = sessionmaker(bind=db_manager.engine)

    def _to_db_hwp(self, hwp: HardwareProfile, session: Session) -> Optional[DbHardwareProfile]:
        if hwp.id:
            db_hwp = session.query(DbHardwareProfile).filter(
                DbHardwareProfile.id == int(hwp.id)).first()
            if not db_hwp:
                return None
        else:
            raise Exception('Creating hwps is currently not supported')
        db_hwp.name = hwp.name
        db_hwp.description = hwp.description
        db_hwp.name_format = hwp.name_format
        db_hwp.resourceAdapterId = hwp.resourceadapter_id
        self._set_db_hwp_tags(db_hwp, hwp.tags)
        return db_hwp

    def _set_db_hwp_tags(self, db_hwp: DbHardwareProfile, tags: Dict[str, str]):
        if not tags:
            tags = {}
        tags_to_delete = {tag.name: tag for tag in db_hwp.tags}
        for name, value in tags.items():
            if name in tags_to_delete.keys():
                tag = tags_to_delete.pop(name)
                tag.value = value
            else:
                db_hwp.tags.append(
                    HardwareProfileTag(name=name, value=value)
                )
        for tag in tags_to_delete.values():
            db_hwp.tags.remove(tag)

    def _to_hwp(self, db_hwp: DbHardwareProfile) -> HardwareProfile:
        return HardwareProfile(
            id=str(db_hwp.id),
            name=db_hwp.name,
            description=db_hwp.description,
            name_format=db_hwp.nameFormat,
            resourceadapter_id=db_hwp.resourceAdapterId,
            tags={tag.name: tag.value for tag in db_hwp.tags}
        )

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[HardwareProfile]:
        logger.debug(
            'list(order_by=%s, order_desc=%s, limit=%s, filters=%s) -> ...',
            order_by, order_desc, limit, filters)
        session = self._Session()
        result = session.query(DbHardwareProfile)
        if order_by:
            #
            # Note: currently, order_alpha is ignored for SqlAlchemy,
            #       as it is the default behavior for strings
            #
            if desc:
                result = result.order_by(desc(getattr(DbHardwareProfile, order_by)))
            else:
                result = result.order_by(getattr(DbHardwareProfile, order_by))
        count = 0
        for db_hwp in result:
            hwp = self._to_hwp(db_hwp)
            if matches_filters(hwp, filters):
                logger.debug('list(...) -> %s', hwp)
                count += 1
                if limit and count == limit:
                    yield hwp
                    session.close()
                    return
                yield hwp

    def get(self, obj_id: str) -> Optional[HardwareProfile]:
        logger.debug('get(obj_id=%s) -> ...', obj_id)

        session = self._Session()
        db_hwp = session.query(DbHardwareProfile).filter(
            DbHardwareProfile.id == int(obj_id)).first()
        hwp = self._to_hwp(db_hwp)
        session.close()

        logger.debug('get(...) -> %s', hwp)
        return hwp

    def save(self, obj: HardwareProfile) -> HardwareProfile:
        logger.debug('save(obj=%s) -> ...', obj)

        hwp_old = None
        if obj.id:
            hwp_old = self.get(obj.id)

        session = self._Session()
        db_hwp = self._to_db_hwp(obj, session)
        if not db_hwp:
            raise Exception('HardwareProfile ID not found: %s', obj.id)
        session.commit()
        hwp = self._to_hwp(db_hwp)
        session.close()

        self._fire_events(hwp_old, hwp)
        logger.debug('save(...) -> %s', hwp)
        return hwp

    def _marshall(self, hwp: HardwareProfile) -> dict:
        schema_class = HardwareProfile.get_schema_class()
        marshalled = schema_class().dump(hwp)
        return marshalled.data

    def _fire_events(self, hwp_old: HardwareProfile, hwp: HardwareProfile):
        self._event_tags_changed(hwp_old, hwp)

    def _event_tags_changed(self, hwp_old: HardwareProfile,
                            hwp: HardwareProfile):
        if hwp_old.tags != hwp.tags:
            HardwareProfileTagsChanged.fire(
                hardwareprofile_id=hwp.id,
                hardwareprofile_name=hwp.name,
                tags=hwp.tags,
                previous_tags=hwp_old.tags
            )
