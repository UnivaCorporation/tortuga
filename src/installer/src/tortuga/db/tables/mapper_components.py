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
from sqlalchemy import Table, Column, Integer, String, Index, ForeignKey
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..components import Components
from ..operatingSystems import OperatingSystems
from ..osComponents import OsComponents
from ..operatingSystemsFamilies import OperatingSystemsFamilies
from ..osFamilyComponents import OsFamilyComponents


class ComponentsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        components_table = Table(
            'Components',
            db_manager.metadata,
            Column('id', Integer, Sequence('components_id_seq'),
                   primary_key=True),
            Column('kitId', Integer,
                   ForeignKey('Kits.id', ondelete='CASCADE'), nullable=False),
            Column('name', String(255), nullable=False),
            Column('version', String(255), nullable=False),
            Column('description', String(255)),
            UniqueConstraint('name', 'kitId'),
            **backend_opts
        )

        Index('Components_kitId', components_table.c.kitId)

        tbl_os_components = db_manager.getMetadataTable('OsComponents')
        tbl_os_family_components = db_manager.getMetadataTable(
            'OsFamilyComponents')

        mapper(Components, components_table, properties={
            'os': relation(
                OperatingSystems, secondary=tbl_os_components),
            'family': relation(
                OperatingSystemsFamilies, secondary=tbl_os_family_components),
            'os_components': relation(
                OsComponents, backref='os_components',
                cascade='all, delete-orphan', passive_deletes=True),
            'osfamily_components': relation(
                OsFamilyComponents, backref='osfamily_components',
                cascade='all, delete-orphan', passive_deletes=True),
        })
