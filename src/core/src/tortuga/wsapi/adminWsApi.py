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

import json
import urllib.request, urllib.parse, urllib.error

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.admin import Admin
from tortuga.objects.tortugaObject import toBool
from .tortugaWsApi import TortugaWsApi


class AdminWsApi(TortugaWsApi):
    """Admin WS API class"""

    def getAdmin(self, adminName):
        """Get admin information

            Returns:
                admin
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """

        url = 'v1/admin/%s' % (urllib.parse.quote_plus(adminName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Admin.getFromDict(responseDict.get(Admin.ROOT_TAG))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getAdminById(self, admin_id):
        """Get admin information

            Returns:
                admin
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """

        url = 'v1/admin/%s' % (admin_id)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Admin.getFromDict(responseDict.get(Admin.ROOT_TAG))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getAdminList(self):
        """Get admin list.

            Returns:
                [admins]
            Throws:
                UserNotAuthorized
                TortugaException
        """

        url = 'v1/admin'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Admin.getListFromDict(responseDict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addAdmin(self, username, password, isCrypted=False, realname=None,
                 description=None): \
            # pylint: disable=too-many-arguments
        """Add an admin using name/password.

        Raises:
            UserNotAuthorized
            FileNotFound
            InvalidXml
            AdminAlreadyExists
            TortugaException
        """

        url = 'v1/admin'

        d = {
            'username': username,
            'password': password,
            'isCrypted': isCrypted,
        }

        if realname is not None:
            d['realname'] = realname

        if description is not None:
            d['description'] = description

        try:
            self.sendSessionRequest(url, method='POST', data=json.dumps(dict(admin=d)))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteAdmin(self, admin):
        """Delete admin.

            Returns:
                None
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """

        url = 'v1/admin/%s' % (urllib.parse.quote_plus(admin))

        try:
            self.sendSessionRequest(url, method='DELETE')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateAdmin(self, adminObject, isCrypted=True):
        """
        Update admin.

            Returns:
                None
            Throws:
                UserNotAuthorized
                AdminNotFound
                TortugaException
        """

        url = 'v1/admin/%s' % (adminObject.getId())

        d = {
            'admin': adminObject.getCleanDict(),
            'isCrypted': isCrypted,
        }

        realname = adminObject.getRealname()
        if realname is not None:
            d['realname'] = realname

        description = adminObject.getDescription()
        if description is not None:
            d['description'] = description

        postdata = json.dumps(d)

        try:
            self.sendSessionRequest(url, method='PUT', data=postdata)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def authenticate(self, adminUsername, adminPassword):
        """
        Check if the credentials are valid.

            Returns:
                True if username and password match a valid user in the system
            Throws:
                UserNotAuthorized
                TortugaException
        """

        url = 'v1/authenticate/%s' % (urllib.parse.quote_plus(adminUsername))

        postdata = json.dumps({
            'password': adminPassword,
        })

        try:
            _, responseDict = self.sendSessionRequest(
                url, method='POST', data=postdata)

            return toBool(responseDict.get('authenticate'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
