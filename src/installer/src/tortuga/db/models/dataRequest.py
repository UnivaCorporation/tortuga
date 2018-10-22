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

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import ModelBase


class DataRequest(ModelBase):
    __tablename__ = 'data_requests'

    id = Column(Integer, primary_key=True)
    request = Column(Text, nullable=False)
    timestamp = Column(DateTime)
#    last_update = Column(DateTime)
    state = Column(String(255), nullable=False, default='pending')
    addHostSession = Column(String(36))
#    message = Column(Text)
#    action = Column(String(255), nullable=False)
