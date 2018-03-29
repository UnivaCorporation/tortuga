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

# pylint: disable=too-few-public-methods

from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from .base import ModelBase


class Nic(ModelBase):
    __tablename__ = 'nics'
    __table_args = {
        UniqueConstraint('mac', 'ip'),
    }

    id = Column(Integer, primary_key=True)
    nodeId = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    networkId = Column(Integer, ForeignKey('networks.id'))
    networkDeviceId = Column(Integer, ForeignKey('networkdevices.id'))
    mac = Column(String(45))
    ip = Column(String(45))
    boot = Column(Boolean, default=False)

    nics_nodeId = index_property('nodeId', 'Nics_nodeId')
    nics_networkId = index_property('networkId', 'Nics_networkId')
    nics_networkDeviceId = index_property(
        'networkDeviceId', 'Nics_networkDeviceId')

    network = relationship('Network', uselist=False, lazy=False,
                           backref='nics')
    networkdevice = relationship('NetworkDevice', uselist=False, lazy=False,
                                 backref='nics')
