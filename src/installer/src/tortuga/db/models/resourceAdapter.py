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

from typing import Dict

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from tortuga.exceptions.resourceNotFound import ResourceNotFound
from tortuga.objects.resource_adapter_settings import BaseSetting

from .base import ModelBase


class ResourceAdapter(ModelBase):
    __tablename__ = 'resourceadapters'
    __table_args__ = (
        UniqueConstraint('name', 'kitId'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    kitId = Column(Integer, ForeignKey('kits.id'))

    kit = relationship('Kit')

    @property
    def settings(self) -> Dict[str, BaseSetting]:
        """
        Returns all possible settings for this resource adapter.

        :return dict: a dict of all settings, where the keys are the
                      name of the setting, and the value is an instance of
                      totrgua.objects.resource_adapter_settings.BaseSetting

        """
        from tortuga.resourceAdapter.resourceAdapterFactory import \
            get_resourceadapter_class
        try:
            ra_class = get_resourceadapter_class(self.name)
        except ResourceNotFound:
            return {}
        return ra_class.settings

    def __repr__(self):
        return '<ResourceAdapter(name=[{}])>'.format(self.name)
