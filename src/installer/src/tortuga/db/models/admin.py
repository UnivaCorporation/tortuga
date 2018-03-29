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

from sqlalchemy import Column, Integer, String

from .base import ModelBase


class Admin(ModelBase):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    realname = Column(String(255))
    description = Column(String(255))

    def __init__(self, username=None, password=None, realname=None,
                 description=None):
        super().__init__()

        self.username = username
        self.password = password
        self.realname = realname
        self.description = description

    def __repr__(self):
        return self.username
