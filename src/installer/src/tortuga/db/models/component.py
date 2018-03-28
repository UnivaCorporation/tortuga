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

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from tortuga.kit.utils import format_component_descriptor

from .base import ModelBase


class Component(ModelBase):
    __tablename__ = 'components'
    __table_args__ = (
        UniqueConstraint('name', 'kitId'),
    )

    id = Column(Integer, primary_key=True)
    kitId = Column(Integer, ForeignKey('kits.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)
    description = Column(String(255))

    components_KitId = index_property('kitId', 'Components_kitId')

    os = relationship('OperatingSystem', secondary='os_components')
    family = relationship('OperatingSystemFamily',
                          secondary='osfamily_components')
    os_components = relationship('OsComponent', backref='os_components',
                                 cascade='all, delete-orphan',
                                 passive_deletes=True)
    osfamily_components = relationship('OsFamilyComponent',
                                       backref='osfamily_components',
                                       cascade='all, delete-orphan',
                                       passive_deletes=True)

    def __init__(self, name=None, version=None, description=None,
                 kitId=None):
        super().__init__()

        self.name = name
        self.version = version
        self.description = description
        self.kitId = kitId

    def __repr__(self):
        return format_component_descriptor(self.name, self.version)
