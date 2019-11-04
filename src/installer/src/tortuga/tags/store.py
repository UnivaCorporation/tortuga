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
from typing import Iterator, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, sessionmaker

from tortuga.db.dbManager import DbManager
from tortuga.db.models.nodeTag import NodeTag
from tortuga.db.models.hardwareProfileTag import HardwareProfileTag
from tortuga.db.models.softwareProfileTag import SoftwareProfileTag
from tortuga.db.models.tagMixin import TagMixin
from tortuga.events.types import HardwareProfileTagsChanged, \
    NodeTagsChanged, SoftwareProfileTagsChanged, TagCreated, TagUpdated, \
    TagDeleted
from tortuga.node.manager import NodeStoreManager
from tortuga.node.types import Node
from tortuga.types.base import BaseType
from tortuga.softwareprofile.manager import SoftwareProfileStoreManager
from tortuga.softwareprofile.types import SoftwareProfile
from tortuga.hardwareprofile.manager import HardwareProfileStoreManager
from tortuga.hardwareprofile.types import HardwareProfile
from tortuga.objectstore.base import matches_filters
from tortuga.typestore.base import TypeStore
from .types import Tag


logger = logging.getLogger(__name__)


class SqlalchemySessionTagStore(TypeStore):
    """
    An implementation of the TypeStore class for Tag objects, backed
    by an Sqlalchemy database session.

    """
    type_class = Tag

    def __init__(self, db_manager: DbManager):
        self._Session = sessionmaker(bind=db_manager.engine)

    def _to_db_tag(self, tag: Tag, session: Session) -> Optional[TagMixin]:
        if not tag.id:
            raise Exception('Tag ID required')
        object_type, object_id, tag_name = Tag.parse_id(tag.id)

        #
        # If tag doesn't already exist, create it
        #
        db_tag = self._get_db_tag(session, object_type, object_id, tag_name)
        if not db_tag:
            if object_type == 'node':
                db_tag = NodeTag(
                    node_id=int(object_id),
                    name=tag_name
                )
            elif object_type == 'softwareprofile':
                db_tag = SoftwareProfileTag(
                    softwareprofile_id=int(object_id),
                    name=tag_name
                )
            elif object_type == 'hardwareprofile':
                db_tag = HardwareProfileTag(
                    hardwareprofile_id=int(object_id),
                    name=tag_name
                )
            else:
                raise Exception('Unsupported object_type: '.format(
                    object_type))

            session.add(db_tag)
            
        db_tag.value = tag.value
        
        return db_tag

    def _get_db_tag(self, session: Session, object_type: str, object_id: str,
                    tag_name: str) -> Optional[TagMixin]:
        try:
            int(object_id)
        except ValueError:
            return None

        if object_type == 'node':
            db_tag = session.query(NodeTag).filter(
                NodeTag.node_id == int(object_id),
                NodeTag.name == tag_name
            ).first()
        elif object_type == 'softwareprofile':
            db_tag = session.query(SoftwareProfileTag).filter(
                SoftwareProfileTag.softwareprofile_id == int(object_id),
                SoftwareProfileTag.name == tag_name
            ).first()
        elif object_type == 'hardwareprofile':
            db_tag = session.query(HardwareProfileTag).filter(
                HardwareProfileTag.hardwareprofile_id == int(object_id),
                HardwareProfileTag.name == tag_name
            ).first()
        else:
            raise Exception('Unsupported object_type: '.format(
                object_type))

        return db_tag

    def _to_tag(self, db_tag: TagMixin) -> Tag:
        tag = Tag(
            value=db_tag.value
        )
        
        if isinstance(db_tag, NodeTag):
            tag.id = 'node:{}:{}'.format(db_tag.node_id, db_tag.name)
        elif isinstance(db_tag, SoftwareProfileTag):
            tag.id = 'softwareprofile:{}:{}'.format(db_tag.softwareprofile_id,
                                                    db_tag.name)
        elif isinstance(db_tag, HardwareProfileTag):
            tag.id = 'hardwareprofile:{}:{}'.format(db_tag.hardwareprofile_id,
                                                    db_tag.name)
        
        return tag

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[Tag]:
        logger.debug(
            'list(order_by=%s, order_desc=%s, limit=%s, filters=%s) -> ...',
            order_by, order_desc, limit, filters)
        
        session = self._Session()
        result_nodes = session.query(NodeTag)
        result_swps = session.query(SoftwareProfileTag)
        result_hwps = session.query(HardwareProfileTag)

        if order_by in ['id', 'object_type']:
            order_by = None
        if order_by == ['object_id']:
            order_by = 'id'
        if order_by:
            #
            # Note: currently, order_alpha is ignored for SqlAlchemy,
            #       as it is the default behavior for strings
            #
            if desc:
                result_nodes = result_nodes.order_by(
                    desc(getattr(NodeTag, order_by)))
                result_swps = result_nodes.order_by(
                    desc(getattr(SoftwareProfileTag, order_by)))
                result_hwps = result_nodes.order_by(
                    desc(getattr(HardwareProfileTag, order_by)))
            else:
                result_nodes = result_nodes.order_by(
                    getattr(NodeTag, order_by))
                result_swps = result_nodes.order_by(
                    getattr(SoftwareProfileTag, order_by))
                result_hwps = result_nodes.order_by(
                    getattr(HardwareProfileTag, order_by))

        count = 0
        for result in [result_nodes, result_swps, result_hwps]:
            for db_tag in result:
                tag = self._to_tag(db_tag)
                if matches_filters(tag, filters):
                    logger.debug('list(...) -> %s', tag)
                    count += 1
                    if limit and count == limit:
                        yield tag
                        session.close()
                        return
                    yield tag
    
    def get(self, tag_id: str) -> Optional[Tag]:
        logger.debug('get(obj_id=%s) -> ...', tag_id)

        object_type, object_id, tag_name = Tag.parse_id(tag_id)

        session = self._Session()
        db_tag = self._get_db_tag(session, object_type, object_id, tag_name)
        tag = None
        if db_tag:
            tag = self._to_tag(db_tag)
        session.close()

        logger.debug('get(...) -> %s', tag)
        return tag

    def save(self, tag: Tag) -> Tag:
        logger.debug('save(tag=%s) -> ...', tag)

        if not tag.id:
            raise Exception('Tag ID not set')
        object_type, object_id, tag_name = Tag.parse_id(tag.id)

        session = self._Session()
        db_tag_old = self._get_db_tag(session, object_type, object_id,
                                      tag_name)
        created = True
        tag_old = None
        if db_tag_old:
            tag_old = self._to_tag(db_tag_old)
            created = False

        if object_type == 'node':
            obj_store = NodeStoreManager.get()
        elif object_type == 'softwareprofile':
            obj_store = SoftwareProfileStoreManager.get()
        elif object_type == 'hardwareprofile':
            obj_store = HardwareProfileStoreManager.get()
        else:
            raise Exception(
                'Unsupported object_type: '.format(object_type))
        obj_old = obj_store.get(object_id)

        db_tag = self._to_db_tag(tag, session)
        if not db_tag:
            raise Exception('Tag ID not found: %s', tag.id)
        session.commit()
        tag = self._to_tag(db_tag)
        session.close()

        #
        # Fire tag events
        #
        if created:
            self._event_tag_created(tag)
        else:
            self._event_tag_updated(tag_old, tag)
        #
        # Fire object events
        #
        obj = obj_store.get(object_id)
        self._fire_object_events(obj_old, obj)

        logger.debug('save(...) -> %s', tag)
        return tag

    def delete(self, tag_id: str):
        logger.debug('delete(tag_id=%s) -> ...', tag_id)

        session = self._Session()
        object_type, object_id, tag_name = Tag.parse_id(tag_id)
        db_tag = self._get_db_tag(session, object_type, object_id, tag_name)
        #
        # If tag not found, do nothing
        #
        if not db_tag:
            session.close()
            return
        tag = self._to_tag(db_tag)

        if object_type == 'node':
            obj_store = NodeStoreManager.get()
            obj_old = obj_store.get(object_id)
        elif object_type == 'softwareprofile':
            obj_store = SoftwareProfileStoreManager.get()
            obj_old = obj_store.get(object_id)
        elif object_type == 'hardwareprofile':
            obj_store = HardwareProfileStoreManager.get()
            obj_old = obj_store.get(object_id)

        else:
            raise Exception('Unsupported object_type: '.format(object_type))

        session.delete(db_tag)
        session.commit()
        session.close()

        self._event_tag_deleted(tag)
        obj = obj_store.get(object_id)
        self._fire_object_events(obj_old, obj)

    def _marshall(self, tag: Tag) -> dict:
        schema_class = Tag.get_schema_class()
        marshalled = schema_class().dump(tag)
        return marshalled.data

    def _fire_object_events(self, obj_old: BaseType, obj: BaseType):
        if isinstance(obj_old, Node) and isinstance(obj, Node):
            self._event_node_tags_changed(obj_old, obj)
        elif isinstance(obj_old, SoftwareProfile) and \
                isinstance(obj, SoftwareProfile):
            self._event_softwareprofile_tags_changed(obj_old, obj)
        elif isinstance(obj_old, HardwareProfile) and \
                isinstance(obj, HardwareProfile):
            self._event_hardwareprofile_tags_changed(obj_old, obj)

    def _event_node_tags_changed(self, node_old: Node, node: Node):
        if node_old.tags != node.tags:
            NodeTagsChanged.fire(
                node_id=node.id,
                node_name=node.name,
                tags=node.tags,
                previous_tags=node_old.tags
            )

    def _event_softwareprofile_tags_changed(self, swp_old: SoftwareProfile,
                                            swp: SoftwareProfile):
        if swp_old.tags != swp.tags:
            SoftwareProfileTagsChanged.fire(
                softwareprofile_id=swp_old.id,
                softwareprofile_name=swp.name,
                tags=swp.tags,
                previous_tags=swp_old.tags,
            )
    
    def _event_hardwareprofile_tags_changed(self, hwp_old: HardwareProfile,
                                            hwp: HardwareProfile):
        if hwp_old.tags != hwp.tags:
            HardwareProfileTagsChanged.fire(
                hardwareprofile_id=hwp.id,
                hardwareprofile_name=hwp.name,
                tags=hwp.tags,
                previous_tags=hwp_old.tags,
            )

    def _event_tag_created(self, tag: Tag):
        TagCreated.fire(
            tag_id=tag.id,
            value=tag.value
        )

    def _event_tag_updated(self, tag_old: Tag, tag: Tag):
        TagUpdated.fire(
            tag_id=tag.id,
            value=tag.value,
            previous_value=tag_old.value
        )

    def _event_tag_deleted(self, tag: Tag):
        TagDeleted.fire(
            tag_id=tag.id,
            value=tag.value
        )
