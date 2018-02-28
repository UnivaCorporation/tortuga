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

from sqlalchemy import Sequence, UniqueConstraint
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..components import Components
from ..kits import Kits
from ..kitSources import KitSources


class KitsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        kits_table = Table(
            'Kits',
            db_manager.metadata,
            Column('id', Integer, Sequence('kits_id_seq'), primary_key=True),
            Column('name', String(45), nullable=False),
            Column('version', String(20), nullable=False),
            Column('iteration', String(20)),
            Column('description', String(255)),
            Column('isOs', Boolean, default=False),
            Column('isRemovable', Boolean, default=False),
            UniqueConstraint('name', 'version', 'iteration'),
            **backend_opts
        )

        mapper(Kits, kits_table, properties={
            'sources': relation(KitSources, backref='kit'),
            'components': relation(Components, backref='kit',
                                   cascade='all, delete-orphan',
                                   passive_deletes=True),
        })


class KitSourcesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        kitsources_table = Table(
            'KitSources',
            db_manager.metadata,
            Column('id', Integer, primary_key=True),
            Column('kitId', Integer, ForeignKey('Kits.id')),
            Column('description', String(255)),
            Column('url', String(255)),
            **backend_opts
        )

        mapper(KitSources, kitsources_table)
