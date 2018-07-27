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

import base64
import json
import urllib.parse
from typing import List, Optional

from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.eula import Eula
from tortuga.objects.kit import Kit

from .tortugaWsApi import TortugaWsApi


class KitWsApi(TortugaWsApi):
    """
    Kit WS API class.
    """

    def getKit(self, name: str, version: Optional[str] = None,
               iteration: Optional[str] = None) -> Kit:
        """
        Get kit info.

        Raises:
            KitNotFound
        """

        url = 'v1/kits/?name={}'.format(urllib.parse.quote_plus(name))

        if version is not None:
            url += '&version={}'.format(
                urllib.parse.quote_plus(version))

        if iteration is not None:
            url += '&iteration={}'.format(
                urllib.parse.quote_plus(iteration))

        try:
            _, responseDict = self.sendSessionRequest(url)

            # response is a list, so reference first item in list
            kits = responseDict.get('kits')
            if not kits:
                kit_spec_str = name

                if version:
                    kit_spec_str += '-{}'.format(version)

                if iteration:
                    kit_spec_str += '-{}'.format(iteration)

                raise KitNotFound(
                    'Kit matching specification [{}] not found'.format(
                        kit_spec_str))

            return Kit.getFromDict(kits[0])
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getKitById(self, id_: int) -> Kit:
        """
        Get kit info by kitId.

        Raises:
            KitNotFound
            TortugaException
        """

        url = 'v1/kits/%s' % (id_)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Kit.getFromDict(responseDict.get('kit'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getKitList(self):
        """
        Get kit list.

            Returns:
                [kits]
            Throws:
                TortugaException
        """

        url = 'v1/kits/'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Kit.getListFromDict(responseDict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def installKit(self, name, version, iteration=None, key=None):
        """
        Install kit using kit name/version/iteration.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """

        dbVersion = '%s-%s' % (version, iteration)

        if not iteration:
            dbVersion = '%s' % (version)

        url = 'v1/kits/%s/%s/%s' % (name, dbVersion, key)

        try:
            _, responseDict = self.sendSessionRequest(url, method='POST')

            return responseDict.get('kitId')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def installKitPackage(self, packageUrl, key=None):
        """
            Install kit package.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaAlreadyExists
        """

        url = 'v1/kit_packages/%s/%s' % (
            base64.b64encode(packageUrl.encode()), key)

        try:
            _, responseDict = self.sendSessionRequest(url, method='POST')

            return responseDict.get('kitId')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getKitEula(self, name, version, iteration=None):
        """
            Fetch eula information for kit.

            Returns:
                eula tortuga object
            Throws:
                UserNotAuthorized
                FileNotFound
                NoKitEula
                TortugaException
        """

        dbVersion = '%s-%s' % (version, iteration)

        if not iteration:
            dbVersion = '%s' % (version)

        url = 'v1/kits/%s/%s/eula' % (name, dbVersion)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Eula.getFromDict(responseDict.get('eula'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getKitPackageEula(self, packageUrl):
        """
            Fetch eula information for kit package.

            Returns:
                eula tortuga object
            Throws:
                UserNotAuthorized
                FileNotFound
                NoKitEula
                TortugaException
        """

        url = 'v1/kit_packages/%s/eula' % (base64.b64encode(packageUrl))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Eula.getFromDict(responseDict.get('eula'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteKit(self, name: str, version: Optional[str] = None,
                  iteration: Optional[str] = None,
                  force: Optional[bool] = False) -> None:
        """
        Delete kit using kit name/version/iteration.

        Raises:
            KitNotFound

        """
        url = 'v1/kits/?name={}'.format(urllib.parse.quote_plus(name))

        if version:
            url += '&version={}'.format(urllib.parse.quote_plus(version))

        if iteration:
            url += '&iteration={}'.format(urllib.parse.quote_plus(iteration))

        url += '&force={}'.format(1 if force else 0)

        try:
            self.sendSessionRequest(url, method='DELETE')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def installOsKit(self, os_media_urls: List[str], **kwargs) -> None: \
            # pylint: disable=unused-argument
        """
        Install kit using kit name/version/iteration.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """

        url = 'v1/kit_os'

        data = json.dumps({
            'mediaUrl': os_media_urls,
        })

        try:
            self.sendSessionRequest(url, method='POST', data=data)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
