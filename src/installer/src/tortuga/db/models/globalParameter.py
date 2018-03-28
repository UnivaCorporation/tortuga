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

from sqlalchemy import Column, Integer, Sequence, String

from .base import ModelBase


class GlobalParameter(ModelBase):
    __tablename__ = 'global_parameters'

    id  = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    value = Column(String(255))
    description = Column(String(255))
