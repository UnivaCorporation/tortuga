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

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import ModelBase


class ResourceAdapterConfig(ModelBase):
    __tablename__ = 'resource_adapter_config'
    __table_args__ = (
        UniqueConstraint('name', 'admin_id', 'resourceadapter_id'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    admin_id = Column(ForeignKey('admins.id'))
    resourceadapter_id = Column(ForeignKey('resourceadapters.id'))

    admin = relationship('Admin', uselist=False,
                         backref='resource_adapter_config')

    resourceadapter = relationship('ResourceAdapter',
                                   uselist=False,
                                   backref='resource_adapter_config')

    settings = relationship('ResourceAdapterSetting',
                            back_populates='resource_adapter_config',
                            cascade='all,delete-orphan')
