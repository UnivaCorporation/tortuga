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

from .base import ModelBase


class Partition(ModelBase):
    __tablename__ = 'partitions'
    __table_args__ = (
        UniqueConstraint('softwareProfileId', 'name', 'device'),
    )

    id = Column(Integer, primary_key=True)
    softwareProfileId = Column(Integer,
                               ForeignKey('softwareprofiles.id'),
                               nullable=False)
    name = Column(String(255), nullable=False)
    device = Column(String(255), nullable=False)
    mountPoint = Column(String(255))
    fsType = Column(String(20), nullable=False)
    size = Column(Integer, nullable=False)
    options = Column(String(255))
    preserve = Column(Boolean, default=False)
    bootLoader = Column(Boolean, default=False)
    diskSize = Column(Integer, nullable=False, default=8000)
    directAttachment = Column(String(255), nullable=False, default='local')
    indirectAttachment = Column(String(255), nullable=False, default='default')
    sanVolume = Column(String(255))
    grow = Column(Boolean, default=False)
    maxSize = Column(Integer)

    partitions_softwareProfileId = index_property(
        'softwareProfileId', 'Partitions_softwareProfileId'
    )
