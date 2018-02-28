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

import pytest
from sqlalchemy import create_engine
from tortuga.db.dbManager import DbManagerBase


def create_db():
    engine = create_engine('sqlite:///:memory:', echo=False)

    dbm = DbManagerBase(engine)

    dbm.init_database()

    return dbm


@pytest.fixture(scope='session')
def dbm():
    return create_db()


@pytest.fixture(scope='class')
def dbm_class(request, dbm):
    request.cls.dbm = dbm
