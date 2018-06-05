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
from sqlalchemy.orm import backref, relationship

from .base import ModelBase


class InstanceMapping(ModelBase):
    __tablename__ = 'instance_mappings'

    id = Column(Integer, primary_key=True)
    resourceadapter_id = Column(Integer, ForeignKey('resourceadapters.id'))
    instance = Column(String)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship('Node', back_populates='instance')

    instance_metadata = relationship('InstanceMetadata',
                                     back_populates='instance')

    resource_adapter_configuration_id = \
        Column(Integer, ForeignKey('resource_adapter_config.id'))

    resource_adapter_configuration = relationship('ResourceAdapterConfig')
