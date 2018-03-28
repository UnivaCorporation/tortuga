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
from sqlalchemy.orm import relationship, backref

from .base import ModelBase


class OperatingSystemFamily(ModelBase):
    __tablename__ = 'operatingsystemsfamilies'
    __table_args__ = (
        UniqueConstraint('name', 'version', 'arch'),
    )

    id = Column(Integer, primary_key=True)
    parentId = Column(Integer, ForeignKey('operatingsystemsfamilies.id'))
    name = Column(String(20), nullable=False)
    version = Column(String(20))
    arch = Column(String(20))

    children = relationship('OperatingSystemFamily',
                            backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return ('<OperatingSystemFamily(name=[%s], version=[%s],'
                ' arch=[%s])>' % (self.name, self.version, self.arch))
