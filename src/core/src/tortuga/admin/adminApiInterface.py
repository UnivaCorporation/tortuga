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

from tortuga.exceptions.abstractMethod import AbstractMethod


class AdminApiInterface(object):
    """
    Admin API interface.
    """

    def getAdmin(self, adminName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get admin information.

            Returns:
                rule
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """
        raise AbstractMethod(
            'getAdmin() has to be implemented in the concrete API class.')

    def getAdminList(self): \
            # pylint: disable=no-self-use
        """
        Get admin list.

            Returns:
                [rules]
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod(
            'getAdminList() has to be implemented in the concrete'
            ' API class.')

    def addAdmin(self, name, password, isCrypted=False, realname=None,
                 description=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Add an admin using rule name/password.

        realname and description fields are informational and optional

            Returns:
                ruleId
            Throws:
                UserNotAuthorized
                FileNotFound
                InvalidXml
                AdminAlreadyExists
                TortugaException
        """
        raise AbstractMethod(
            'addAdmin() has to be implemented in the concrete API class.')

    def deleteAdmin(self, name): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete admin.

            Returns:
                None
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """
        raise AbstractMethod(
            'updateAdmin() has to be implemented in the concrete API'
            ' class.')

    def updateAdmin(self, adminObject, isCrypted=True): \
            # pylint: disable=no-self-use,unused-argument
        """
        Update admin.

            Returns:
                None
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """
        raise AbstractMethod(
            'updateAdmin() has to be implemented in the concrete API'
            ' class.')

    def authenticate(self, adminUsername, adminPassword): \
            # pylint: disable=no-self-use,unused-argument
        """
        Check if the credentials are valid.

            Returns:
                True if username and password match a valid user in the system
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod(
            'authenticate() has to be implemented in the concrete API'
            ' class.')
