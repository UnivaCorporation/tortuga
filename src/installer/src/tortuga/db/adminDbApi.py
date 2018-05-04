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

from tortuga.db.adminsDbHandler import AdminsDbHandler
from tortuga.db.dbManager import DbManager
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.adminNotFound import AdminNotFound
from tortuga.objects.admin import Admin


class AdminDbApi(TortugaDbApi):
    """
    Admin DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._adminsDbHandler = AdminsDbHandler()

    def getAdmin(self, name):
        """
        Get admin from the db.

            Returns:
                Admin tortuga object
            Throws:
                AdminNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            return Admin.getFromDbDict(
                self._adminsDbHandler.getAdmin(session, name).__dict__)
        finally:
            DbManager().closeSession()

    def getAdminById(self, admin_id):
        """
        Get admin from the db.

            Returns:
                Admin tortuga object
            Throws:
                AdminNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            return Admin.getFromDbDict(
                self._adminsDbHandler.getAdminById(
                    session, admin_id).__dict__)
        finally:
            DbManager().closeSession()

    def getAdminList(self):
        """
        Get list of all admins from the db.

            Returns:
                [adminTortugaObject]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbList = self._adminsDbHandler.getAdminList(session)

            return self.getTortugaObjectList(Admin, dbList)
        finally:
            DbManager().closeSession()

    def addAdmin(self, name, password, realname=None, description=None):
        """
        Insert an admin into the db.

            Returns:
                admin tortuga object
            Throws:
                AdminAlreadyExists
                DbError
        """

        session = DbManager().openSession()

        try:
            self._adminsDbHandler.addAdmin(
                session, name, password, realname, description)

            session.commit()
        except Exception:
            session.rollback()

            raise
        finally:
            DbManager().closeSession()

    def deleteAdmin(self, name):
        """
        Delete admin from the db.

            Returns:
                None
            Throws:
                AdminNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            self._adminsDbHandler.deleteAdmin(session, name)

            session.commit()
        except Exception:
            session.rollback()

            raise
        finally:
            DbManager().closeSession()

    def updateAdmin(self, admin):
        """
        Update existing admin.

            Returns:
                None
            Throws:
                AdminNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            if admin.getId() is not None:
                # User specified the admin id, use it to positively
                # identify the admin user.
                dbAdmin = self._adminsDbHandler.getAdminById(
                    session, admin.getId())
            elif admin.getUsername() is not None:
                dbAdmin = self._adminsDbHandler.getAdmin(
                    session, admin.getUsername())
            else:
                raise AdminNotFound(
                    'Ambiguous admin request (neither id nor username'
                    ' specified)')

            if admin.getUsername() is not None:
                dbAdmin.username = admin.getUsername()

            if admin.getPassword() is not None:
                dbAdmin.password = admin.getPassword()

            if admin.getRealname() is not None:
                dbAdmin.realname = admin.getRealname()

            if admin.getDescription() is not None:
                dbAdmin.description = admin.getDescription()

            self._adminsDbHandler.updateAdmin(session, dbAdmin)

            session.commit()
        except Exception:
            session.rollback()

            raise
        finally:
            DbManager().closeSession()
