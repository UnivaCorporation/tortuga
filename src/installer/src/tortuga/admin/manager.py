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

from random import choice
import string

from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.auth.manager import AuthManager
from tortuga.db.adminDbApi import AdminDbApi


class AdminManager(TortugaObjectManager):
    """
    Class for cluster admin management

    """
    RANDOM_PASSWORD_LENGTH = 16

    def __init__(self):
        super(AdminManager, self).__init__()

        self._adminDbApi = AdminDbApi()

    def getAdmin(self, adminName):
        return self._adminDbApi.getAdmin(adminName)

    def getAdminById(self, admin_id):
        return self._adminDbApi.getAdminById(admin_id)

    def getAdminList(self):
        return self._adminDbApi.getAdminList()

    def addAdmin(self, name, password, isCrypted, realname=None,
                 description=None):
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
        if not password:
            password = self._generate_random_password()
            isCrypted = False

        if not isCrypted:
            password = AuthManager().cryptPassword(password)

        self._adminDbApi.addAdmin(name, password, realname, description)

        AuthManager().reloadPrincipals()

    def _generate_random_password(self) -> str:
        """
        Generates a random password, RANDOM_PASSWORD_LENGTH characters long.

        :return str: the random password

        """
        string_chars: str = string.ascii_letters + string.digits
        return ''.join(
            [choice(string_chars) for _ in
             range(AdminManager.RANDOM_PASSWORD_LENGTH)]
        )

    def deleteAdmin(self, admin):
        self._adminDbApi.deleteAdmin(admin)

        AuthManager().reloadPrincipals()

    def updateAdmin(self, adminObject, isCrypted):
        if adminObject.getPassword() is not None:
            # Only consider updating the password if the field is defined
            if not isCrypted:
                adminObject.setPassword(
                    AuthManager().cryptPassword(
                        adminObject.get_password()))

        self._adminDbApi.updateAdmin(adminObject)

        AuthManager().reloadPrincipals()
