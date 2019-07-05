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

from tortuga.db.dbManager import DbManager
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
        self._db_manager = db_manager

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[Node]:
        logger.debug(
            'list(order_by={}, order_desc={}, limit, filters={}) -> ...'.format(
                order_by, order_desc, limit, filters
            )
        )
        with self._db_manager.session() as session:
            result = session.query(Node)
            if order_by:
                #
                # Note: currently, order_alpha is ignored for SqlAlchemy,
                #       as it is the default behavior for strings
                #
                if desc:
                    result = result.order_by(desc(getattr(Node, order_by)))
                else:
                    result = result.order_by(getattr(Node, order_by))
            count = 0
            for _, node in result:
                if matches_filters(node, filters):
                    count += 1
                    if limit and count == limit:
                        yield node
                        return
                    yield node

    def get(self, obj_id: str) -> Optional[Node]:
        with self._db_manager.session() as session:
            node = session.query(Node.id == int(obj_id)).one_or_none()
        return node

    def save(self, obj: Node) -> Node:
        with self._db_manager.session() as session:
            #
            # If the obj does not have an ID, then it is a create...
            #
            if not obj.id:
                session.add(obj)
            #
            # Otherwise it is an update
            #
            else:
                #
                # Dump the incoming object as a dict
                #
                obj_dict = obj.schema().dump(obj).data
                #
                # Lookup the existing instance
                #
                node = session.query(Node.id == obj.id).one()
                #
                # Load load the incoming data into the existing
                # instance
                #
                node = self.type_class.schema().load(obj_dict,
                                                     session=session,
                                                     instance=node).data
        return node
