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

from sqlalchemy import Column, ForeignKey, Integer, String, Text, \
    UniqueConstraint
from sqlalchemy.orm import relationship, validates

from .base import ModelBase


class ResourceAdapterSetting(ModelBase):
    """Resource adapter key-value setting pair."""

    __tablename__ = 'resource_adapter_settings'
    __table_args__ = (
        UniqueConstraint('key', 'resource_adapter_config_id'),
    )

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    resource_adapter_config_id = Column(
        Integer, ForeignKey('resource_adapter_config.id'))
    resource_adapter_config = relationship(
        "ResourceAdapterConfig", back_populates='configuration')

    @validates('key')
    def normalize(self, key, value): \
            # pylint: disable=unused-argument,no-self-use
        """Ensure 'key' is always lowercase."""
        return value.lower()

    def __repr__(self):
        return ('<ResourceAdapterSetting(resource_adapter_config=[{}]:'
                ' {}={})>'.format(
                    self.resource_adapter_config.name, self.key, self.value))
