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
from sqlalchemy import (Table, Column, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..admins import Admins
from ..kits import Kits
from ..resourceAdapters import ResourceAdapters
from ..resourceAdapterCredentials import ResourceAdapterCredentials


class ResourceAdaptersTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        resourceadapters_table = Table(
            'ResourceAdapters',
            db_manager.metadata,
            Column('id', Integer, Sequence('resourceadapters_id_seq'),
                   primary_key=True),
            Column('name', String(45), nullable=False),
            Column('kitId', Integer, ForeignKey('Kits.id')),
            UniqueConstraint('name', 'kitId'),
            **backend_opts
        )

        mapper(ResourceAdapters, resourceadapters_table, properties={
            'kit': relation(Kits)})


class ResourceAdapterCredentialsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        resourceadaptercredentials_table = Table(
            'resourceadaptercredentials',
            db_manager.metadata,
            Column('id', Integer, Sequence('resadaptercreds_id_seq'),
                   primary_key=True),
            Column('name', String(255), nullable=False),
            # Column('description', String(255)),
            Column('admin_id', ForeignKey('Admins.id')),
            Column('resourceadapter_id', ForeignKey('ResourceAdapters.id')),
            Column('key', String(255), nullable=False),
            Column('value', String(255)),
            UniqueConstraint('name', 'admin_id', 'key', 'resourceadapter_id'),
            **backend_opts
        )

        mapper(ResourceAdapterCredentials, resourceadaptercredentials_table,
               properties={
                   'admin': relation(Admins, uselist=False,
                                     backref='credentials'),
                   'resourceadapter': relation(ResourceAdapters,
                                               uselist=False,
                                               backref='credentials')
               })
