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

# pylint: disable=not-callable,multiple-statements,no-member

from sqlalchemy.orm.exc import NoResultFound
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.admins import Admins
from tortuga.exceptions.adminAlreadyExists import AdminAlreadyExists
from tortuga.exceptions.adminNotFound import AdminNotFound
from tortuga.exceptions.deleteAdminFailed import DeleteAdminFailed


class AdminsDbHandler(TortugaDbObjectHandler):
    """
    This class handles global admins table.
    """

    def getAdmin(self, session, name):
        """
        Return admin.
        """

        self.getLogger().debug('Retrieving admin user [%s]' % name)

        try:
            return session.query(
                Admins).filter(Admins.username == name).one()
        except NoResultFound:
            raise AdminNotFound('Admin user [%s] not found' % (name))

    def getAdminById(self, session, admin_id):
        """
        Return admin.

        Raises:
            AdminNotFound
        """

        dbAdmin = session.query(Admins).get(admin_id)

        if not dbAdmin:
            raise AdminNotFound('Admin ID [%s] not found' % (admin_id))

        return dbAdmin

    def getAdminList(self, session):
        """
        Get list of admins from the db.
        """

        return session.query(Admins).all()

    def addAdmin(self, session, name, password, realname=None,
                 description=None):
        """
        Insert admin into the db.

        Raises:
            AdminAlreadyExists
        """

        # Check if admin already exists before attempting to add
        try:
            self.getAdmin(session, name)

            raise AdminAlreadyExists(
                'Admin user [%s] already exists' % (name))
        except AdminNotFound:
            pass

        dbAdmin = Admins(
            username=name, password=password, realname=realname,
            description=description)

        session.add(dbAdmin)

    def deleteAdmin(self, session, admin):
        """
        Delete admin from the db.

        Raises:
            AdminNotFound
        """

        # If 'admin' is a digit, treat it like a primary key, otherwise
        # treat it as a admin username.
        dbAdmin = self.getAdminById(session, admin) \
            if admin.isdigit() else self.getAdmin(session, admin)

        # Make sure this admin is not associated with anything
        if dbAdmin.softwareprofiles:
            sps = [sp.name for sp in dbAdmin.softwareprofiles]

            raise DeleteAdminFailed(
                'User [%s] is admin of software profile(s): [%s]' % (
                    dbAdmin.username, ' '.join(sps)))

        if dbAdmin.hardwareprofiles:
            hps = [hp.name for hp in dbAdmin.hardwareprofiles]

            raise DeleteAdminFailed(
                'User [%s] is admin of hardware profile(s): [%s]' % (
                    dbAdmin.username, ' '.join(hps)))

        session.delete(dbAdmin)

    def updateAdmin(self, session, dbAdmin):
        """
        Update an existing admin.

        Raises:
            AdminAlreadyExists
        """

        dbOldAdmin = self.getAdminById(session, dbAdmin.id)

        # If admin name is changing, ensure there is presently not an
        # admin with the new name.

        if dbAdmin.username != dbOldAdmin.username:
            try:
                self.getAdmin(session, dbAdmin.username)

                raise AdminAlreadyExists(
                    'Admin [%s] already exists' % (dbAdmin.username))
            except AdminNotFound:
                # OK.
                pass
