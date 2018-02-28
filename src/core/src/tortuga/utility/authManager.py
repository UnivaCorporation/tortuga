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

import os
import crypt
from tortuga.exceptions.userNotAuthorized import UserNotAuthorized
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.config.configManager import ConfigManager
from tortuga.utility.authPrincipal import AuthPrincipal
from tortuga.admin.adminApiFactory import getAdminApi
from tortuga.types import Singleton


def authorizeRoot():
    if os.getuid() != 0:
        raise UserNotAuthorized('Command must be run as \'root\' user.')


class AuthManager(TortugaObjectManager, Singleton):
    def __init__(self):
        super(AuthManager, self).__init__()

        self._configManager = ConfigManager()

        self.__principals = {}

        self.__loadPrincipals()

    def cryptPassword(self, cleartext, salt="$1$"): \
            # pylint: disable=no-self-use
        """ Return crypted password.... """
        return crypt.crypt(cleartext, salt)

    def reloadPrincipals(self):
        """ This is used to reload the principals in auth manager """
        self.__principals.clear()

        self.__loadPrincipals()

    def __loadPrincipals(self):
        """ Load principals for config manager and datastore """
        # Create builtin cfm principal
        cfmUser = AuthPrincipal(
            self._configManager.getCfmUser(),
            self.cryptPassword(self._configManager.getCfmPassword()),
            {'roles': 'cfm'})

        # Add cfm user
        self.__principals[cfmUser.getName()] = cfmUser

        # Add users from DB
        if self._configManager.isInstaller():
            for admin in getAdminApi().getAdminList():
                self.__principals[admin.getUsername()] = AuthPrincipal(
                    admin.getUsername(), admin.getPassword(),
                    attributeDict={'id': admin.getId()})

    def getPrincipal(self, username, password):
        """ Get a principal based on a username and password """
        principal = self.__principals.get(username)
        if principal and principal.getPassword() == crypt.crypt(
                password, principal.getPassword()):
            return principal

        return None
