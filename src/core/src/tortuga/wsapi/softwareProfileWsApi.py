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
import urllib.error
import urllib.parse
import urllib.request

from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.component import Component
from tortuga.objects.node import Node
from tortuga.objects.softwareProfile import SoftwareProfile

from .tortugaWsApi import TortugaWsApi


class SoftwareProfileWsApi(TortugaWsApi):
    """
    SoftwareProfile WS API class.
    """
    def getSoftwareProfile(self, softwareProfileName, optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        url = 'v1/softwareProfiles?name=%s' % (softwareProfileName)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return SoftwareProfile.getListFromDict(responseDict)[0]
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getSoftwareProfileById(self, swProfileId, optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        url = 'v1/softwareProfiles/%d' % (swProfileId)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return SoftwareProfile.getFromDict(
                responseDict.get('softwareprofile'))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise SoftwareProfileNotFound(
                    'Software profile ID [%s] not found' % (swProfileId))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getSoftwareProfileList(self, tags=None):
        """
        Returns a list of all software profiles in the system.
        """

        url = 'v1/softwareProfiles'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return SoftwareProfile.getListFromDict(responseDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getEnabledComponentList(self, name):
        """
        Get the list of components enabled for a given softwareprofile

            Returns:
               a list of enabled components
            Throws:
                TortugaException
        """

        url = 'v1/softwareProfiles/%s/components' % (
            urllib.parse.quote_plus(name))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Component.getListFromDict(responseDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNodeList(self, softwareProfileName):
        """
        Return list of nodes contained within specified software profile
        """

        url = 'v1/softwareProfiles/%s/nodes' % (
            urllib.parse.quote_plus(softwareProfileName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Node.getListFromDict(responseDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addUsableHardwareProfileToSoftwareProfile(self,
                                                  hardwareProfileName,
                                                  softwareProfileName):
        """
        Add hardware profile to software profile

            Returns:
                SoftwareUsesHardwareID
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """

        url = 'v1/softwareProfiles/%s/mappings/%s' % (
            urllib.parse.quote_plus(softwareProfileName),
            urllib.parse.quote_plus(hardwareProfileName))

        try:
            response, _ = self.sendSessionRequest(url, method='POST')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateSoftwareProfile(self, softwareProfileObject):
        """
        Update the given Software Profile by calling WS API
        """

        url = 'v1/softwareProfiles/%s' % (softwareProfileObject.getId())

        postdata = json.dumps(softwareProfileObject.getCleanDict())

        try:
            self.sendSessionRequest(url, method='PUT', data=postdata)
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addAdmin(self, softwareProfileName, adminUsername):
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """

        url = 'v1/softwareProfiles/%s/admin/%s' % (
            urllib.parse.quote_plus(softwareProfileName),
            urllib.parse.quote_plus(adminUsername))

        try:
            response, _ = self.sendSessionRequest(
                url, method='POST')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteAdmin(self, softwareProfileName, adminUsername):
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """

        url = 'v1/softwareProfiles/%s/admin/%s' % (
            urllib.parse.quote_plus(softwareProfileName),
            urllib.parse.quote_plus(adminUsername))

        try:
            response, _ = self.sendSessionRequest(
                url, method='DELETE')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def enableComponent(self, softwareProfileName, kitName, kitVersion,
                        kitIteration, componentName, componentVersion=None,
                        sync=True):
        """
        Enable a component on a given software profile

            Returns:
                None
            Throws:
                TortugaException
                SoftwareProfileNotFound
                KitNotFound
                ComponentNotFound
                ComponentAlreadyEnabled
        """

        url = 'v1/softwareProfiles/%s/enable_components' % (
            urllib.parse.quote_plus(softwareProfileName))

        postdata = {
            'components': [
                {
                    'kitName': kitName,
                    'kitVersion': kitVersion,
                    'kitIteration': kitIteration,
                    'componentName': componentName,
                    'componentVersion': componentVersion,
                },
            ],
            'sync': sync,
        }

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(postdata))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def disableComponent(self, softwareProfileName, kitName, kitVersion,
                         kitIteration, componentName, componentVersion=None,
                         sync=True):
        """
        Disable a component on a given software profile

            Returns:
                None
            Throws:
                TortugaException
                SoftwareProfileNotFound
                KitNotFound
                ComponentNotFound
        """

        url = 'v1/softwareProfiles/%s/disable_components' % (
            urllib.parse.quote_plus(softwareProfileName))

        postdata = {
            'components': [
                {
                    'kitName': kitName,
                    'kitVersion': kitVersion,
                    'kitIteration': kitIteration,
                    'componentName': componentName,
                    'componentVersion': componentVersion,
                },
            ],
            'sync': sync,
        }

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(postdata))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def createSoftwareProfile(self, swProfile, settingsDict=None):
        """
        Create software profile from template

            Returns:
                None
            Throws:
                TortugaException
        """

        url = 'v1/softwareProfiles'

        postdata = json.dumps({
            'softwareProfile': swProfile.getCleanDict(),
            'settingsDict': settingsDict or {},
        })

        try:
            response, _ = self.sendSessionRequest(
                url, method='POST', data=postdata)

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteUsableHardwareProfileFromSoftwareProfile(
            self, hardwareProfileName, softwareProfileName):
        """
        Delete useable hardware profile

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                HardwareProfileNotFound
                TortugaException
        """

        url = 'v1/softwareProfiles/%s/mappings/%s' % (
            urllib.parse.quote_plus(softwareProfileName),
            urllib.parse.quote_plus(hardwareProfileName))

        try:
            response, _ = self.sendSessionRequest(
                url, method='DELETE')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteSoftwareProfile(self, softwareProfileName):
        """
        Delete software profile

            Returns:
                N/A
            Throws:
                TortugaException
        """

        url = 'v1/softwareProfiles/%s' % (
            urllib.parse.quote_plus(softwareProfileName))

        try:
            response, _ = self.sendSessionRequest(
                url, method='DELETE')

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        """
        Copy software profile

            Returns:
                N/A
            Throws:
                TortugaException
        """

        url = 'v1/softwareProfiles/%s/copy' % (
            urllib.parse.quote_plus(srcSoftwareProfileName))

        postdata = json.dumps({
            'dstSoftwareProfileName': dstSoftwareProfileName,
        })

        try:
            response, _ = self.sendSessionRequest(
                url, method='POST', data=postdata)

            return response
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getUsableNodes(self, softwareProfileName):
        url = 'v1/softwareProfiles/%s/usable' % (
            urllib.parse.quote_plus(softwareProfileName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Node.getListFromDict(responseDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
