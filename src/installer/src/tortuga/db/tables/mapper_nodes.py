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

from sqlalchemy import Sequence
from sqlalchemy import (Table, Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..admins import Admins
from ..nics import Nics
from ..nodes import Nodes
from ..nodeRequests import NodeRequests
from ..nodeTags import NodeTags
from ..tags import Tags


class NodesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        nodes_table = Table(
            'Nodes',
            db_manager.metadata,
            Column('id', Integer, Sequence('nodes_id_seq'), primary_key=True),
            Column('name', String(45), unique=True, nullable=False),
            Column('state', String(20)),
            Column('bootFrom', Integer, default=0),
            Column('lastUpdate', String(20)),
            Column('rack', Integer, default=0),
            Column('rank', Integer, default=0),
            Column('hardwareProfileId', Integer,
                   ForeignKey('HardwareProfiles.id')),
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id')),
            Column('lockedState', String(20), nullable=False,
                   default='Unlocked'),
            Column('parentNodeId', Integer, ForeignKey('Nodes.id')),
            Column('maxChildUnits', Integer, default=0),
            Column('myUnits', Integer, default=1),
            Column('isIdle', Boolean, nullable=False, default=True),
            Column('destSPId', Integer),
            Column('addHostSession', String(36)),
            **backend_opts
        )

        Index('Nodes_parentNodeId',
              nodes_table.c.parentNodeId)
        Index('Nodes_softwareProfileId',
              nodes_table.c.softwareProfileId)
        Index('Nodes_hardwareProfileId',
              nodes_table.c.hardwareProfileId)
        Index('Nodes_addHostSession',
              nodes_table.c.addHostSession)

        mapper(Nodes, nodes_table, properties={
            'nics': relation(Nics, backref='node', lazy=False),
            'parentnode': relation(Nodes, backref='children',
                                   remote_side=[nodes_table.c.id]),
            'tags': relation(
                Tags,
                primaryjoin=nodes_table.c.id ==
                            db_manager.metadata.tables[
                                'node_tags'].c.node_id,
                secondary=db_manager.metadata.tables['node_tags'],
                backref='nodes'),

        })


class NodeRequestsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        tbl = Table(
            'NodeRequests',
            db_manager.metadata,
            Column('id', Integer, Sequence('node_requests_id_seq'),
                   primary_key=True),
            Column('request', Text, nullable=False),
            Column('timestamp', DateTime),
            Column('last_update', DateTime),
            Column('state', String(255), nullable=False),
            Column('addHostSession', String(36)),
            Column('message', Text),
            Column('admin_id', Integer, ForeignKey('Admins.id')),
            Column('action', String(255), nullable=False),
            **backend_opts)

        mapper(NodeRequests, tbl, properties={
            'owner': relation(Admins),
        })


class NodeTagsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        node_tags_table = Table('node_tags',
                                db_manager.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('node_id', Integer,
                                       ForeignKey('Nodes.id'),
                                       nullable=False),
                                Column('tag_id', Integer,
                                       ForeignKey('tags.id'),
                                       nullable=False),
                                UniqueConstraint('node_id', 'tag_id'),
                                **backend_opts)

        mapper(NodeTags, node_tags_table)
