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

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from .base import ModelBase
from .tagMixin import TagMixin


class NodeTag(TagMixin, ModelBase):
    __tablename__ = 'node_tags'
    __table_args__ = (UniqueConstraint('node_id', 'name'),)

    node_id = Column(Integer, ForeignKey('nodes.id'))
