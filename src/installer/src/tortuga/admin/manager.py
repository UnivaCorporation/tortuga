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

from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.auth.manager import AuthManager
from tortuga.db.adminDbApi import AdminDbApi


class AdminManager(TortugaObjectManager):
    """Class for cluster admin management"""

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
        if not isCrypted:
            password = AuthManager().cryptPassword(password)

        self._adminDbApi.addAdmin(name, password, realname, description)

        AuthManager().reloadPrincipals()

    def deleteAdmin(self, admin):
        self._adminDbApi.deleteAdmin(admin)

        AuthManager().reloadPrincipals()

    def updateAdmin(self, adminObject, isCrypted):
        if adminObject.get_password() is not None:
            # Only consider updating the password if the field is defined
            if not isCrypted:
                adminObject.setPassword(
                    AuthManager().cryptPassword(
                        adminObject.get_password()))

        self._adminDbApi.updateAdmin(adminObject)

        AuthManager().reloadPrincipals()
