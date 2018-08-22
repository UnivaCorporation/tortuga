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

from typing import Optional, Union

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.hardwareProfile import HardwareProfile

from .tortugaWsApi import TortugaWsApi


class HardwareProfileWsApi(TortugaWsApi):
    """
    Hardware profile WS API class.
    """

    def getHardwareProfile(self, hardwareProfileName: str,
                           optionDict: Optional[Union[dict, None]] = None):
        """
        Get hardware profile by name
        """
        url = 'hardwareprofiles/?name=%s' % (hardwareProfileName)

        if optionDict:
            for key, value in optionDict.items():
                if not value:
                    continue
                url += '&include={}'.format(key)

        try:
            responseDict = self.get(url)
            return HardwareProfile.getListFromDict(responseDict)[0]

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def getHardwareProfileById(self, id_,
                               optionDict: Optional[Union[dict, None]] = None):
        """
        Get hardware profile by name
        """
        url = 'hardwareprofiles/%d' % (id_)

        if optionDict:
            for key, value in optionDict.items():
                if not value:
                    continue
                url += '&include={}'.format(key)

        try:
            responseDict = self.get(url)
            return HardwareProfile.getFromDict(
                responseDict.get('hardwareprofile'))

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateSoftwareOverrideAllowed(self, hardwareProfileName, flag):
        url = 'hardwareprofiles/%s/softwareOverrideAllowed' % (
            hardwareProfileName)

        postdata = {'flag': flag}

        try:
            responseDict = self.post(url, postdata)
            return responseDict

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def getHardwareProfileList(self,
                               optionDict: Optional[Union[dict, None]] = None,
                               tags=None): \
            # pylint: disable=unused-argument
        """
        Get list of hardware profiles by calling WS API
        """

        url = 'hardwareprofiles/'

        # TODO: add support for building query string with 'tags'
        try:
            responseDict = self.get(url)
            return HardwareProfile.getListFromDict(responseDict)

        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateHardwareProfile(self, hardwareProfileObject):
        """
        Update the given Hardware Profile by calling WS API
        """

        url = 'hardwareprofiles/%s' % (hardwareProfileObject.getId())

        try:
            self.put(url, hardwareProfileObject.getCleanDict())

        except Exception as ex:
            raise TortugaException(exception=ex)

    def addAdmin(self, hardwareProfileName, adminUsername):
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """

        url = 'hardwareprofiles/%s/admin/%s' % (
            hardwareProfileName, adminUsername)

        try:
            responseDict = self.post(url)
            return responseDict

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteAdmin(self, hardwareProfileName, adminUsername):
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """

        url = 'hardwareprofiles/%s/admin/%s' % (
            hardwareProfileName, adminUsername)

        try:
            responseDict = self.delete(url)
            return responseDict

        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteHardwareProfile(self, hardwareProfileName):
        """
        Delete hardware profile

            Returns:
                N/A
            Throws:
                TortugaException
        """

        url = 'hardwareprofiles/%s' % (hardwareProfileName)

        try:
            responseDict = self.delete(url)
            return responseDict

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def createHardwareProfile(self, hwProfile: HardwareProfile,
                              settingsDict: Optional[Union[dict, None]] = None):
        """
        Create hardware profile from template

            Returns:
                None
            Throws:
                TortugaException
        """

        url = 'hardwareprofiles/'

        postdata = {
            'hardwareProfile': hwProfile.getCleanDict(),
            'settingsDict': settingsDict,
        }

        try:
            responseDict = self.post(url, postdata)
            return responseDict

        except TortugaException as ex:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def copyHardwareProfile(self, srcHardwareProfileName,
                            dstHardwareProfileName):
        """
        Copy hardware profile

            Returns:
                N/A
            Throws:
                TortugaException
        """

        url = 'hardwareprofiles/{}/copy/{}'.format(
            srcHardwareProfileName, dstHardwareProfileName)

        try:
            responseDict = self.post(url)
            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)
