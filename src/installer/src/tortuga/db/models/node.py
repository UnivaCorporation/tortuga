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

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from .base import ModelBase


class Node(ModelBase):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    public_hostname = Column(String, unique=True, nullable=True)
    state = Column(String, default='Discovered')
    bootFrom = Column(Integer, default=0)
    lastUpdate = Column(String(20))
    rack = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    hardwareProfileId = Column(Integer, ForeignKey('hardwareprofiles.id'))
    softwareProfileId = Column(Integer, ForeignKey('softwareprofiles.id'))
    lockedState = Column(String(20), nullable=False, default='Unlocked')
    isIdle = Column(Boolean, nullable=False, default=True)
    addHostSession = Column(String(36))

    nodes_softwareProfileId = index_property(
        'softwareProfilesId', 'Nodes_softwareProfileId')
    nodes_hardwareProfileId = index_property(
        'hardwareProfilesId', 'Nodes_hardwareProfilesId')
    nodes_addHostSession = index_property(
        'addHostSession', 'Nodes_addHostSession')

    nics = relationship('Nic', backref='node', lazy=False,
                        cascade='all, delete-orphan')

    tags = relationship(
        'Tag',
        secondary='node_tags',
        backref='nodes'
    )

    instance = relationship(
        'InstanceMapping', uselist=False, back_populates='node',
        cascade='all,delete-orphan')

    def __repr__(self):
        return 'Node(name=%s)' % (self.name)
