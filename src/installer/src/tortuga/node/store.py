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
from typing import Dict, Iterator, List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session, sessionmaker

from tortuga.db.dbManager import DbManager
from tortuga.db.models.node import Node as DbNode
from tortuga.db.models.nodeTag import NodeTag
from tortuga.events.types import TagCreated, TagDeleted, TagUpdated, \
    NodeStateChanged, NodeTagsChanged
from tortuga.objectstore.base import matches_filters
from tortuga.typestore.base import TypeStore
from .types import Node

logger = logging.getLogger(__name__)


class SqlalchemySessionNodeStore(TypeStore):
    """
    An implementation of the TypeStore class for Node objects, backed
    by an Sqlalchemy database session.

    """
    type_class = Node

    def __init__(self, db_manager: DbManager):
        self._Session = sessionmaker(bind=db_manager.engine)

    def _to_db_node(
            self,
            node: Node,
            session: Session) -> Tuple[Optional[DbNode], List, List, List]:
        if node.id:
            db_node = session.query(DbNode).filter(
                DbNode.id == int(node.id)).first()
            if not db_node:
                return None, [], [], []
        else:
            raise Exception('Creating nodes is currently not supported')

        db_node.name = node.name
        db_node.public_hostname = node.public_hostname
        db_node.softwareProfileId = int(node.softwareprofile_id)
        db_node.hardwareProfileId = int(node.hardwareprofile_id)
        db_node.state = node.state
        db_node.lockedState = node.locked
        tag_create_events, tag_update_events, tag_delete_events = \
            self._set_db_node_tags(db_node, node.tags)

        return (db_node, tag_create_events, tag_update_events,
                tag_delete_events)

    def _set_db_node_tags(self, db_node: DbNode,
                          tags: Dict[str, str]) -> Tuple[List, List, List]:
        if not tags:
            tags = {}
        create_events = []
        update_events = []
        delete_events = []
        tags_to_delete = {tag.name: tag for tag in db_node.tags}
        for name, value in tags.items():
            if name in tags_to_delete.keys():
                tag = tags_to_delete.pop(name)
                update_events.append({
                    "name": name,
                    "value": value,
                    "previous_value": tag.value
                })
                tag.value = value
            else:
                create_events.append({
                    "name": name,
                    "value": value,
                })
                db_node.tags.append(
                    NodeTag(name=name, value=value)
                )
        for tag in tags_to_delete.values():
            delete_events.append({
                "name": tag.name,
                "value": tag.value
            })
            db_node.tags.remove(tag)

        return create_events, update_events, delete_events

    def _to_node(self, db_node: DbNode) -> Node:
        return Node(
            id=str(db_node.id),
            name=db_node.name,
            public_hostname=db_node.public_hostname,
            softwareprofile_id=str(db_node.softwareProfileId),
            hardwareprofile_id=str(db_node.hardwareProfileId),
            state=db_node.state,
            locked=db_node.lockedState,
            tags={tag.name: tag.value for tag in db_node.tags}
        )

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[Node]:
        logger.debug(
            'list(order_by=%s, order_desc=%s, limit=%s, filters=%s) -> ...',
            order_by, order_desc, limit, filters)
        session = self._Session()
        result = session.query(DbNode)
        if order_by:
            #
            # Note: currently, order_alpha is ignored for SqlAlchemy,
            #       as it is the default behavior for strings
            #
            if desc:
                result = result.order_by(desc(getattr(DbNode, order_by)))
            else:
                result = result.order_by(getattr(DbNode, order_by))
        count = 0
        for db_node in result:
            node = self._to_node(db_node)
            if matches_filters(node, filters):
                logger.debug('list(...) -> %s', node)
                count += 1
                if limit and count == limit:
                    yield node
                    session.close()
                    return
                yield node

    def get(self, obj_id: str) -> Optional[Node]:
        logger.debug('get(obj_id=%s) -> ...', obj_id)

        session = self._Session()
        db_node = session.query(DbNode).filter(
            DbNode.id == int(obj_id)).first()
        node = self._to_node(db_node)
        session.close()

        logger.debug('get(...) -> %s', node)
        return node

    def save(self, obj: Node) -> Node:
        logger.debug('save(obj=%s) -> ...', obj)

        node_old = None
        if obj.id:
            node_old = self.get(obj.id)

        session = self._Session()
        db_node, tag_create_events, tag_update_events, tag_delete_events = \
            self._to_db_node(obj, session)
        if not db_node:
            raise Exception('Node ID not found: %s', obj.id)
        session.commit()
        node = self._to_node(db_node)
        session.close()

        self._fire_node_events(node_old, node)
        self._fire_tag_events(node.id, tag_create_events, tag_update_events,
                              tag_delete_events)
        logger.debug('save(...) -> %s', node)
        return node

    def _marshall(self, node: Node) -> dict:
        schema_class = Node.get_schema_class()
        marshalled = schema_class().dump(node)
        return marshalled.data

    def _fire_node_events(self, node_old: Node, node: Node):
        self._event_state_changed(node_old, node)
        self._event_tags_changed(node_old, node)

    def _event_state_changed(self, node_old: Node, node: Node):
        if node_old.state != node.state:
            NodeStateChanged(node=self._marshall(node),
                             previous_state=node_old.state)

    def _event_tags_changed(self, node_old: Node, node: Node):
        if node_old.tags != node.tags:
            NodeTagsChanged.fire(
                node_id=str(node.id),
                node_name=node.name,
                tags=node.tags,
                previous_tags=node_old.tags
            )

    def _fire_tag_events(self, node_id: str, created: List[Dict],
                         updated: List[Dict], deleted: List[Dict]):
        for evt in created:
            TagCreated.fire(
                tag_id='node:{}:{}'.format(node_id, evt['name']),
                value=evt['value']
            )
        for evt in updated:
            TagUpdated.fire(
                tag_id='node:{}:{}'.format(node_id, evt['name']),
                value=evt['value'],
                previous_value=evt['previous_value']
            )
        for evt in deleted:
            TagDeleted.fire(
                tag_id='node:{}:{}'.format(node_id, evt['name']),
                value=evt['value']
            )
