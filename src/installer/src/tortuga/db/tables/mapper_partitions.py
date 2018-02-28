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
from sqlalchemy import (Table, Boolean, Column, ForeignKey, Index, Integer,
                        String, UniqueConstraint)
from sqlalchemy.orm import mapper

from .mapper import TableMapper
from ..partitions import Partitions


class PartitionsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        partitions_table = Table(
            'Partitions',
            db_manager.metadata,
            Column('id', Integer, Sequence('partitions_id_seq'),
                   primary_key=True),
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id'), nullable=False),
            Column('name', String(255), nullable=False),
            Column('device', String(255), nullable=False),
            Column('mountPoint', String(255)),
            Column('fsType', String(20), nullable=False),
            Column('size', Integer, nullable=False),
            Column('options', String(255)),
            Column('preserve', Boolean, default=False),
            Column('bootLoader', Boolean, default=False),
            Column('diskSize', Integer, nullable=False, default=8000),
            Column('directAttachment', String(255), nullable=False,
                   default='local'),
            Column('indirectAttachment', String(255), nullable=False,
                   default='default'),
            Column('sanVolume', String(255)),
            Column('grow', Boolean, default=False),
            Column('maxSize', Integer),
            UniqueConstraint('softwareProfileId', 'name', 'device'),
            **backend_opts
        )

        Index('Partitions_softwareProfileId',
              partitions_table.c.softwareProfileId)

        mapper(Partitions, partitions_table)
