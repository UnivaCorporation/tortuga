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
from typing import Optional, Union

from tortuga.exceptions.tortugaException import TortugaException
import tortuga.objects.provisioningInfo
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
        url = 'v1/hardwareprofiles/?name=%s' % (hardwareProfileName)

        for key, value in optionDict.items():
            if not value:
                continue
            url += '&include={}'.format(key)

        try:
            _, responseDict = self.sendSessionRequest(url)

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
        url = 'v1/hardwareprofiles/%d' % (id_)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return HardwareProfile.getFromDict(
                responseDict.get('hardwareprofile'))
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateSoftwareOverrideAllowed(self, hardwareProfileName, flag):
        url = 'v1/hardwareprofiles/%s/softwareOverrideAllowed' % (
            hardwareProfileName)

        postdata = json.dumps({
            'flag': flag,
        })

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='POST', data=postdata)

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getHypervisorNodes(self, hardwareProfileName):
        url = 'v1/hardwareprofiles/%s/virtualContainerNodes' % (
            hardwareProfileName)

        try:
            (response, responseDict) = self.sendSessionRequest(url)

            nodeList = []

            if 'nodes' in responseDict:
                nDicts = responseDict.get('nodes')
                for nDict in nDicts:
                    node = tortuga.objects.node.Node.getFromDict(nDict)
                    nodeList.append(node)
            elif 'node' in responseDict:
                node = tortuga.objects.node.Node.getFromDict(
                    responseDict['node'])

                nodeList.append(node)

            return nodeList
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

        url = 'v1/hardwareprofiles/'

        # TODO: add support for building query string with 'tags'
        try:
            _, responseDict = self.sendSessionRequest(url)

            return HardwareProfile.getListFromDict(responseDict)
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateHardwareProfile(self, hardwareProfileObject):
        """
        Update the given Hardware Profile by calling WS API
        """

        url = 'v1/hardwareprofiles/%s' % (hardwareProfileObject.getId())

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='PUT',
                data=json.dumps(hardwareProfileObject.getCleanDict()))
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

        url = 'v1/hardwareprofiles/%s/admin/%s' % (
            hardwareProfileName, adminUsername)

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='POST')

            return response
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

        url = 'v1/hardwareprofiles/%s/admin/%s' % (
            hardwareProfileName, adminUsername)

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='DELETE')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    # def setProvisioningNic(self, hardwareProfileName, nicId):
    #     url = 'hardwareProfiles/%s/provisioningNicId/%s' % (
    #         hardwareProfileName, nicId)
    #
    #     try:
    #         (response, responseDict) = self.sendSessionRequest(
    #             url, method='POST')
    #
    #     except TortugaException:
    #         raise
    #     except Exception as ex:
    #         raise TortugaException(exception=ex)

    def deleteHardwareProfile(self, hardwareProfileName):
        """
        Delete hardware profile

            Returns:
                N/A
            Throws:
                TortugaException
        """

        url = 'v1/hardwareprofiles/%s' % (hardwareProfileName)

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='DELETE')

            return response
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

        url = 'v1/hardwareprofiles/'

        postdata = {
            'hardwareProfile': hwProfile.getCleanDict(),
            'settingsDict': settingsDict,
        }

        try:
            response, _ = self.sendSessionRequest(
                url, method='POST', data=json.dumps(postdata))

            return response
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

        url = 'v1/hardwareprofiles/%s/copy' % (srcHardwareProfileName)

        postdata = {
            'dstHardwareProfileName': dstHardwareProfileName,
        }

        try:
            (response, responseDict) = self.sendSessionRequest(
                url, method='POST', data=json.dumps(postdata))

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
