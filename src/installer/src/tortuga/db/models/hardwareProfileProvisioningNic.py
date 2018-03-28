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


class HardwareProfileProvisioningNic(ModelBase):
    __tablename__ = 'hardwareprofile_provisioning_nics'

    hardwareProfileId = Column(Integer,
                               ForeignKey('hardwareprofiles.id'),
                               nullable=False,
                               primary_key=True)
    nicId = Column(Integer, ForeignKey('nics.id'),
                   nullable=False, primary_key=True)

    hardwareProfileProvisioningNics_hardwareProfileId = index_property(
        'hardwareProfileId',
        'HardwareProfileProvisioningNics_hardwareProfileId'
    )

    hardwareProfileProvisioningNics_nicId = index_property(
        'nicId',
        'HardwareProfileProvisioningNics_nicId'
    )

    nic = relationship('Nic')
    hardwareprofile = relationship('HardwareProfile')
