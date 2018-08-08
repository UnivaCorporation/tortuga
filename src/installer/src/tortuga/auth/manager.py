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

from passlib.hash import pbkdf2_sha256

from sqlalchemy.orm.session import Session
from tortuga.config.configManager import ConfigManager
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.types import Singleton

from .principal import AuthPrincipal


class AuthManager(TortugaObjectManager, Singleton):
    def __init__(self, *, session: Session):
        super(AuthManager, self).__init__()

        self.session = session

        self._configManager = ConfigManager()

        self.__principals = {}

        self.__loadPrincipals()

    def cryptPassword(self, cleartext): \
            # pylint: disable=no-self-use
        """
        Return crypted password
        """

        return pbkdf2_sha256.hash(cleartext)

    def reloadPrincipals(self):
        """
        This is used to reload the principals in auth manager
        """

        self.__principals.clear()

        self.__loadPrincipals()

    def __loadPrincipals(self):
        """
        Load principals for config manager and datastore
        """
        from tortuga.admin.api import AdminApi

        # Create built-in cfm principal
        cfmUser = AuthPrincipal(
            self._configManager.getCfmUser(),
            self.cryptPassword(self._configManager.getCfmPassword()),
            {'roles': 'cfm'})

        # Add cfm user
        self.__principals[cfmUser.get_name()] = cfmUser

        # Add users from DB
        if self._configManager.isInstaller():
            for admin in AdminApi().getAdminList(self.session):
                self.__principals[admin.getUsername()] = AuthPrincipal(
                    admin.getUsername(), admin.getPassword(),
                    attributes={'id': admin.getId()})

    def get_principal(self, username: str) -> AuthPrincipal:
        """
        Get a principal by username.

        :param str username:   the username of the principal to lookup

        :return AuthPrincipal: the principal, if found, otherwise None

        """
        principal: AuthPrincipal = self.__principals.get(username)
        if not principal:
            principal = None

        return principal
