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

from .base import ModelBase


class SoftwareUsesHardware(ModelBase):
    __tablename__ = 'software_uses_hardware'

    id = Column(Integer, primary_key=True)
    softwareProfileId = Column(Integer, ForeignKey('softwareprofiles.id'))
    hardwareProfileId = Column(Integer, ForeignKey('hardwareprofiles.id'))

    softwareUsesHardware_softwareProfileId = index_property(
        'softwareProfileId', 'SoftwareUsesHardware_softwareProfileId'
    )

    softwareUsesHardware_hardwareProfileId = index_property(
        'hardwareProfileId', 'SoftwareUsesHardware_hardwareProfileId'
    )

    def __init__(self, softwareProfileId, hardwareProfileId):
        super().__init__()

        self.softwareProfileId = softwareProfileId
        self.hardwareProfileId = hardwareProfileId
