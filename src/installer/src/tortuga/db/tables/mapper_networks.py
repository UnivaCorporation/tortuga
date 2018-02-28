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
from sqlalchemy import (Table, Boolean, Column, ForeignKey, Index,
                        Integer, String, UniqueConstraint)
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..networkDevices import NetworkDevices
from ..networks import Networks
from ..nics import Nics


class NetworkDevicesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        networkdevices_table = Table(
            'NetworkDevices',
            db_manager.metadata,
            Column('id', Integer, Sequence('networkdevices_id_seq'),
                   primary_key=True),
            Column('name', String(20), nullable=False, unique=True),
            **backend_opts
        )

        mapper(NetworkDevices, networkdevices_table)


class NetworksTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        networks_table = Table(
            'Networks',
            db_manager.metadata,
            Column('id', Integer, Sequence('networks_id_seq'),
                   primary_key=True),
            Column('address', String(45), nullable=False),
            Column('netmask', String(45), nullable=False),
            Column('suffix', String(20)),
            Column('gateway', String(45)),
            Column('options', String(255)),
            Column('name', String(255)),
            Column('startIp', String(45)),
            Column('type', String(20), nullable=False),
            Column('increment', Integer, default=1),
            Column('usingDhcp', Boolean, nullable=False, default=False),
            UniqueConstraint('address', 'netmask'),
            **backend_opts
        )

        mapper(Networks, networks_table)


class NicsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        nics_table = Table(
            'Nics',
            db_manager.metadata,
            Column('id', Integer, Sequence('nics_id_seq'), primary_key=True),
            Column('nodeId', Integer, ForeignKey('Nodes.id'), nullable=False),
            Column('networkId', Integer, ForeignKey('Networks.id')),
            Column('networkDeviceId', Integer,
                   ForeignKey('NetworkDevices.id')),
            Column('mac', String(45)),
            Column('ip', String(45)),
            Column('boot', Boolean, default=False),
            UniqueConstraint('mac', 'ip'),
            **backend_opts
        )

        Index('Nics_nodeId', nics_table.c.nodeId)
        Index('Nics_networkId', nics_table.c.networkId)
        Index('Nics_networkDeviceId', nics_table.c.networkDeviceId)

        mapper(Nics, nics_table, properties={
            'network': relation(
                Networks, uselist=False, lazy=False, backref="nics"),
            'networkdevice': relation(
                NetworkDevices, uselist=False, lazy=False, backref="nics")
        })
