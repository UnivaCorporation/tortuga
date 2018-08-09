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

from tortuga.admin.api import AdminApi
from tortuga.exceptions.adminNotFound import AdminNotFound
from tortuga.exceptions.adminAlreadyExists import AdminAlreadyExists


def test_getAdmin(dbm):
    with dbm.session() as session:
        result = AdminApi().getAdmin(session, 'admin')

    assert result.getUsername() == 'admin' and \
        result.getRealname() == 'realname'


def test_getAdminList(dbm):
    with dbm.session() as session:
        result = AdminApi().getAdminList(session)

    assert 'admin' in [admin.getUsername() for admin in result]


def test_addAdmin(dbm):
    with dbm.session() as session:
        realname = 'Another admin user'

        AdminApi().addAdmin(session, 'testuser', 'password', realname=realname)

        result = AdminApi().getAdmin(session, 'testuser')

        assert result.getUsername() == 'testuser'

        result2 = AdminApi().getAdminById(session, result.getId())

        assert result.getUsername() == result2.getUsername() and \
            result.getRealname() == result2.getRealname()

        with pytest.raises(AdminAlreadyExists):
            AdminApi().addAdmin(session, 'testuser', 'password')

        AdminApi().deleteAdmin(session, 'testuser')

        with pytest.raises(AdminNotFound):
            AdminApi().getAdmin(session, 'testuser')


def test_deleteAdmin(dbm):
    with dbm.session() as session:
        with pytest.raises(AdminNotFound):
            AdminApi().deleteAdmin(session, 'nonexistentuser')


def test_updateAdmin(dbm):
    with dbm.session() as session:
        result = AdminApi().getAdmin(session, 'admin')

        result.setRealname('Joe User')

        AdminApi().updateAdmin(session, result)

        result2 = AdminApi().getAdmin(session, 'admin')

        assert result2.getRealname() == 'Joe User'
