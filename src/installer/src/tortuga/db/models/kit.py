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

from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import ModelBase


class Kit(ModelBase):
    __tablename__ = 'kits'
    __table_args__ = (
        UniqueConstraint('name', 'version', 'iteration'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    version = Column(String(20), nullable=False)
    iteration = Column(String(20))
    description = Column(String(255))
    isOs = Column(Boolean, default=False)
    isRemovable = Column(Boolean, default=False)

    sources = relationship('KitSource', backref='kit')
    components = relationship('Component', backref='kit',
                              cascade='all, delete-orphan',
                              passive_deletes=True)
