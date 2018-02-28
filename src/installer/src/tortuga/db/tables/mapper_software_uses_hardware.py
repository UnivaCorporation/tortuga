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
from sqlalchemy import Table, Column, ForeignKey, Index, Integer
from sqlalchemy.orm import mapper

from .mapper import TableMapper
from ..softwareUsesHardware import SoftwareUsesHardware


class SoftwareUsesHardwareTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        softwareuseshardware_table = Table(
            'SoftwareUsesHardware',
            db_manager.metadata,
            Column('id', Integer, Sequence('softwareuseshardware_id_seq'),
                   primary_key=True),
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id'), nullable=False),
            Column('hardwareProfileId', Integer,
                   ForeignKey('HardwareProfiles.id'), nullable=False),
            **backend_opts
        )

        Index('SoftwareUsesHardware_softwareProfileId',
              softwareuseshardware_table.c.softwareProfileId)

        Index('SoftwareUsesHardware_hardwareProfileId',
              softwareuseshardware_table.c.hardwareProfileId)

        mapper(SoftwareUsesHardware, softwareuseshardware_table)
