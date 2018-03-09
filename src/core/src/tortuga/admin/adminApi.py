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

# pylint: disable=no-member

from tortuga.admin.adminManager import AdminManager
from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException


class AdminApi(TortugaApi):
    """Admin API class"""

    def __init__(self):
        super(AdminApi, self).__init__()

        self._adminManager = AdminManager()

    def getAdmin(self, adminName):
        """Get an admin by name"""

        try:
            return self._adminManager.getAdmin(adminName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error getting admin [{0}]'.format(adminName))

            raise TortugaException(exception=ex)

    def getAdminById(self, admin_id):
        """Get an admin by name"""

        try:
            return self._adminManager.getAdminById(admin_id)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error getting admin by id [{0}]'.format(admin_id))

            raise TortugaException(exception=ex)

    def getAdminList(self):
        """Return list of admin users"""

        try:
            return self._adminManager.getAdminList()
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Error getting admin list')

            raise TortugaException(exception=ex)

    def addAdmin(self, name, password, isCrypted=False, realname=None,
                 description=None):
        """Add a new admin to the system"""

        try:
            self._adminManager.addAdmin(
                name, password, isCrypted, realname, description)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteAdmin(self, admin):
        """Delete an existing admin from the system"""

        try:
            return self._adminManager.deleteAdmin(admin)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def updateAdmin(self, adminObject, isCrypted=True):
        """Update an existing admin in the system"""

        try:
            self._adminManager.updateAdmin(adminObject, isCrypted)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def authenticate(self, adminUsername, adminPassword):
        """Check if the credentials are valid.

            Returns:
                True if username and password match a valid user in the system
            Throws:
                UserNotAuthorized
                TortugaException
        """

        try:
            return self._adminManager.authenticate(
                adminUsername, adminPassword)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error authenticating admin [{0}]'.format(adminUsername))

            raise TortugaException(exception=ex)
