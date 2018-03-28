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

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from .base import ModelBase


class HardwareProfileNetwork(ModelBase):
    __tablename__ = 'hardwareprofile_networks'

    hardwareProfileId = Column(Integer,
                               ForeignKey('hardwareprofiles.id'),
                               primary_key=True)
    networkId = Column(Integer, ForeignKey('networks.id'),
                       primary_key=True, index=True)
    networkDeviceId = Column(Integer,
                             ForeignKey('networkdevices.id'),
                             primary_key=True, index=True)

    networkdevice = relationship('NetworkDevice', lazy=False)
    network = relationship('Network', backref="hardwareprofilenetworks",
                           lazy=False)
