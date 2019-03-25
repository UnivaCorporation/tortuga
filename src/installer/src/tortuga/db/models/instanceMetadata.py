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

from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import backref, relationship

from .base import ModelBase


class InstanceMetadata(ModelBase):
    __tablename__ = 'instance_metadata'
    __table_args__ = (
        UniqueConstraint('instance_id', 'key'),
    )

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255))
    instance_id = Column(Integer, ForeignKey('instance_mappings.id'))

    instance = relationship('InstanceMapping',
                            back_populates='instance_metadata')

    def __repr__(self):
        return ('<InstanceMetadata(key=[{}], value=[{}],'
                ' instance_id=[[}])>'.format(
                    self.key, self.value, self.instance_id))
