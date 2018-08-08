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

from tortuga.admin.manager import AdminManager
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.utility.tortugaApi import TortugaApi
from sqlalchemy.orm.session import Session


class AdminApi(TortugaApi):
    """Admin API class"""

    def __init__(self):
        super(AdminApi, self).__init__()

        self._adminManager = AdminManager()

    def getAdmin(self, session: Session, adminName):
        """Get an admin by name"""

        try:
            return self._adminManager.getAdmin(session, adminName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error getting admin [{0}]'.format(adminName))

            raise TortugaException(exception=ex)

    def getAdminById(self, session: Session, admin_id):
        """Get an admin by name"""

        try:
            return self._adminManager.getAdminById(session, admin_id)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error getting admin by id [{0}]'.format(admin_id))

            raise TortugaException(exception=ex)

    def getAdminList(self, session: Session):
        """Return list of admin users"""

        try:
            return self._adminManager.getAdminList(session)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Error getting admin list')

            raise TortugaException(exception=ex)

    def addAdmin(self, session: Session, name, password=None,
                 isCrypted=False, realname=None, description=None):
        """
        Adds an admin user.

        :param str name:        the admin username
        :param str password:    the admin password, if None, a random one is
                                generated
        :param bool isCrypted:  if False, the password is encrypted before
                                saving
        :param str realname:    the full/real name for the user
        :param str description: the description of the user

        """
        try:
            self._adminManager.addAdmin(
                session, name, password, isCrypted, realname, description)

        except TortugaException:
            raise

        except Exception as ex:
            self.getLogger().exception('addAdmin failed')
            raise TortugaException(exception=ex)

    def deleteAdmin(self, session: Session, admin):
        """Delete an existing admin from the system"""

        try:
            return self._adminManager.deleteAdmin(session, admin)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('deleteAdmin failed')
            raise TortugaException(exception=ex)

    def updateAdmin(self, session: Session, adminObject, isCrypted=True):
        """Update an existing admin in the system"""

        try:
            self._adminManager.updateAdmin(session, adminObject, isCrypted)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('updateAdmin failed')
            raise TortugaException(exception=ex)
