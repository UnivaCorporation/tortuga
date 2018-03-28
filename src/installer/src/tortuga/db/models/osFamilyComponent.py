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

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from .base import ModelBase


class OsFamilyComponent(ModelBase):
    __tablename__ = 'osfamily_components'

    id = Column(Integer, primary_key=True)
    osFamilyId = Column(Integer,
                        ForeignKey('operatingsystemsfamilies.id',
                                   ondelete='CASCADE'))
    componentId = Column(Integer,
                         ForeignKey('components.id', ondelete='CASCADE'))

    osFamilyComponents_componentId = index_property(
        'componentId', 'OsFamilyComponents_componentId'
    )

    osFamilyComponents_osFamilyId = index_property(
        'osFamilyId', 'OsFamilyComponents_osFamilyId'
    )

    family = relationship('OperatingSystemFamily', lazy=False)
