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

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .base import ModelBase

softwareprofile_admins = Table(
    'softwareprofile_admins',
    ModelBase.metadata,
    Column('softwareProfileId', Integer,
           ForeignKey('softwareprofiles.id'), nullable=False,
           primary_key=True),
    Column('adminId', Integer, ForeignKey('admins.id'),
           nullable=False, primary_key=True)
)


class SoftwareProfile(ModelBase):
    __tablename__ = 'softwareprofiles'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False, unique=True)
    description = Column(String(255))
    kernel = Column(String(255))
    kernelParams = Column(String(512))
    initrd = Column(String(255))
    osId = Column(Integer, ForeignKey('operatingsystems.id'), nullable=False)
    type = Column(String(20), nullable=False)
    minNodes = Column(Integer)
    isIdle = Column(Boolean, nullable=False, default=False)

    admins = relationship(
        'Admin', backref='softwareprofiles',
        secondary='softwareprofile_admins')

    components = relationship(
        'Component',
        secondary='softwareprofile_components', backref='softwareprofiles')

    nodes = relationship('Node', backref='softwareprofile')

    os = relationship('OperatingSystem', lazy=False)

    partitions = relationship('Partition', cascade="all,delete-orphan")

    hardwareprofiles = relationship(
        'HardwareProfile',
        secondary='software_uses_hardware',
        lazy=False,
        backref='mappedsoftwareprofiles')

    hwprofileswithidle = relationship(
        'HardwareProfile',
        foreign_keys='HardwareProfile.idleSoftwareProfileId',
        backref='idlesoftwareprofile'
    )

    children = relationship(
        'HardwareProfile',
        foreign_keys='HardwareProfile.hypervisorSoftwareProfileId',
        backref='hypervisor'
    )

    kitsources = relationship(
        'KitSource',
        secondary='softwareprofile_kitsources',
        backref='softwareprofiles'
    )

    tags = relationship(
        'Tag',
        secondary='softwareprofile_tags',
        backref='softwareprofiles'
    )

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<SoftwareProfile(name=%s)>' % (self.name)
