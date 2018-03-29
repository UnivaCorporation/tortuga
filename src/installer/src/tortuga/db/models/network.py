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

from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint

from .base import ModelBase


class Network(ModelBase):
    __tablename__ = 'networks'
    __table_args = {
        UniqueConstraint('address', 'netmask'),
    }

    id = Column(Integer, primary_key=True)
    address = Column(String(45), nullable=False)
    netmask = Column(String(45), nullable=False)
    suffix = Column(String(20))
    gateway = Column(String(45))
    options = Column(String(255))
    name = Column(String(255))
    startIp = Column(String(45))
    type = Column(String(20), nullable=False)
    increment = Column(Integer, default=1)
    usingDhcp = Column(Boolean, nullable=False, default=False)
