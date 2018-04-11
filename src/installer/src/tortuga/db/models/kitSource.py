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

from sqlalchemy import Column, ForeignKey, Integer, String

from .base import ModelBase


class KitSource(ModelBase):
    __tablename__ = 'kitsources'

    id = Column(Integer, primary_key=True)
    kitId = Column(Integer, ForeignKey('kits.id'))
    description = Column(String(255))
    url = Column(String(255))

    def __init__(self, name=None, version=None, iteration=None,
                 description=None, isOs=None, isRemovable=None): \
            # pylint: disable=too-many-arguments
        super().__init__()

        self.name = name
        self.version = version
        self.iteration = iteration
        self.description = description
        self.isOs = isOs
        self.isRemovable = isRemovable

    def __repr__(self):
        return '<KitSource(description=[%s], url=[%s])>' % (
            self.description, self.url)
