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
from sqlalchemy import (Table, Column, ForeignKey, Index, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import backref, mapper, relation

from .mapper import TableMapper
from ..operatingSystems import OperatingSystems
from ..operatingSystemsFamilies import OperatingSystemsFamilies
from ..osComponents import OsComponents
from ..osFamilyComponents import OsFamilyComponents


class OperatingSystemsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        operatingsystems_table = Table(
            'OperatingSystems',
            db_manager.metadata,
            Column('id', Integer, Sequence('operatingsystems_id_seq'),
                   primary_key=True),
            Column('familyId', Integer,
                   ForeignKey('OperatingSystemsFamilies.id')),
            Column('name', String(20), nullable=False),
            Column('version', String(20)),
            Column('arch', String(20)),
            UniqueConstraint('name', 'version', 'arch'),
            **backend_opts
        )

        tbl2 = db_manager.getMetadataTable('OperatingSystemsFamilies')

        mapper(OperatingSystems, operatingsystems_table, properties={
            'family': relation(
                OperatingSystemsFamilies,
                lazy=False,
                uselist=False,
                primaryjoin=operatingsystems_table.c.familyId == tbl2.c.id)
        })


class OsComponentsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        oscomponents_table = Table(
            'OsComponents',
            db_manager.metadata,
            Column('id', Integer, Sequence('oscomponents_id_seq'),
                   primary_key=True),
            Column('osId', Integer,
                   ForeignKey('OperatingSystems.id', ondelete='CASCADE'),
                   nullable=False),
            Column('componentId', Integer,
                   ForeignKey('Components.id', ondelete='CASCADE'),
                   nullable=False),
            UniqueConstraint('osId', 'componentId'),
            **backend_opts
        )

        Index('OsComponents_componentId', oscomponents_table.c.componentId)
        Index('OsComponents_osId', oscomponents_table.c.osId)

        mapper(OsComponents, oscomponents_table, properties={
            'os': relation(OperatingSystems, lazy=False),
        })


class OperatingSystemsFamiliesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        operatingsystemsfamilies_table = Table(
            'OperatingSystemsFamilies',
            db_manager.metadata,
            Column('id', Integer, Sequence('operatingsystemsfamilies_id_seq'),
                   primary_key=True),
            Column('parentId', Integer,
                   ForeignKey('OperatingSystemsFamilies.id')),
            Column('name', String(20), nullable=False),
            Column('version', String(20)),
            Column('arch', String(20)),
            UniqueConstraint('name', 'version', 'arch'),
            **backend_opts
        )

        mapper(
            OperatingSystemsFamilies, operatingsystemsfamilies_table,
            properties={
                'children': relation(
                    OperatingSystemsFamilies,
                    backref=backref(
                        'parent',
                        remote_side=[operatingsystemsfamilies_table.c.id]))
            })


class OsFamilyComponentsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        osfamilycomponents_table = Table(
            'OsFamilyComponents',
            db_manager.metadata,
            Column('id', Integer, Sequence('osfamilycomponents_id_seq'),
                   primary_key=True),
            Column('osFamilyId', Integer,
                   ForeignKey('OperatingSystemsFamilies.id',
                              ondelete='CASCADE')),
            Column('componentId', Integer,
                   ForeignKey('Components.id', ondelete='CASCADE')),
            **backend_opts
        )

        Index('OsFamilyComponents_componentId',
              osfamilycomponents_table.c.componentId)
        Index('OsFamilyComponents_osFamilyId',
              osfamilycomponents_table.c.osFamilyId)

        mapper(OsFamilyComponents, osfamilycomponents_table, properties={
            'family': relation(OperatingSystemsFamilies, lazy=False),
        })
