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

from tortuga.softwareprofile.softwareProfileManager \
    import SoftwareProfileManager
from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException


class SoftwareProfileApi(TortugaApi): \
        # pylint: disable=too-many-public-methods
    """
    SoftwareProfile API class.
    """

    def __init__(self):
        super(SoftwareProfileApi, self).__init__()

        self._softwareProfileManager = SoftwareProfileManager()

    def getSoftwareProfile(self, softwareProfileName, optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                getSoftwareProfile(softwareProfileName, optionDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getSoftwareProfileById(self, softwareProfileId, optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                getSoftwareProfileById(softwareProfileId, optionDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteSoftwareProfile(self, softwareProfileName):
        """
        Delete the specified software profile

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            self._softwareProfileManager.\
                deleteSoftwareProfile(softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getSoftwareProfileList(self, tags=None):
        """
        Returns a list of all software profiles.
        """
        try:
            return self._softwareProfileManager.\
                getSoftwareProfileList(tags=tags)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getIdleSoftwareProfileList(self):
        """
        Get software profile information

            Returns:
               idle softwareProfile list
            Throws:
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                getIdleSoftwareProfileList()
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def setIdleState(self, softwareProfileName, state):
        """
        Get idle state information

            Returns:
               -none-
            Throws:
                TortugaException
        """
        try:
            self._softwareProfileManager.\
                setIdleState(softwareProfileName, state)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getEnabledComponentList(self, name):
        """
        Get enabled component list..

            Returns:
                list of enabled components
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                getEnabledComponentList(name)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getPartitionList(self, softwareProfileName):
        """
        Get partition list for a given softwareprofile

            Returns:
                [partition]
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                getPartitionList(softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def addUsableHardwareProfileToSoftwareProfile(self,
                                                  hardwareProfileName,
                                                  softwareProfileName):
        """
        Set useable hardware profile

            Returns:
                SoftwareUsesHardwareID
            Throws:
                SoftwareProfileNotFound
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.\
                addUsableHardwareProfileToSoftwareProfile(
                    hardwareProfileName, softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                       hardwareProfileName,
                                                       softwareProfileName):
        """
        Delete useable hardware profile

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                HardwareProfileNotFound
                TortugaException
        """
        try:
            self._softwareProfileManager.\
                deleteUsableHardwareProfileFromSoftwareProfile(
                    hardwareProfileName, softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            self._softwareProfileManager.\
                addAdmin(softwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            self._softwareProfileManager.\
                deleteAdmin(softwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def updateSoftwareProfile(self, softwareProfileObject):
        """
        Update a software profile in the database that matches the passed
        in software profile object.  The ID is used as the primary matching
        criteria.

            Returns:
                None
            Throws:
                TortugaException
        """
        try:
            self._softwareProfileManager.\
                updateSoftwareProfile(softwareProfileObject)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def createSoftwareProfile(self, swProfileSpec, settingsDict=None):
        try:
            self._softwareProfileManager.createSoftwareProfile(
                swProfileSpec, settingsDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getNodeList(self, softwareProfileName):
        try:
            return self._softwareProfileManager.getNodeList(
                softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def enableComponent(self, softwareProfileName, kitName, kitVersion,
                        kitIteration, compName, compVersion=None, sync=True):
        try:
            return self._softwareProfileManager.enableComponent(
                softwareProfileName,
                kitName,
                kitVersion,
                kitIteration,
                compName,
                compVersion,
                sync=sync)
        except Exception as ex:
            if not isinstance(ex, TortugaException):
                self.getLogger().exception(
                    'Exception raised in {0}.enableComponent()'.format(
                        self.__class__.__name__))

                # Wrap exception
                raise TortugaException(exception=ex)

            raise

    def disableComponent(self, softwareProfileName, kitName, kitVersion,
                         kitIteration, compName, compVersion=None, sync=True):
        try:
            return self._softwareProfileManager.disableComponent(
                softwareProfileName,
                kitName,
                kitVersion,
                kitIteration,
                compName,
                compVersion,
                sync=sync)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        try:
            return self._softwareProfileManager.\
                copySoftwareProfile(
                    srcSoftwareProfileName, dstSoftwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getUsableNodes(self, softwareProfileName):
        try:
            return self._softwareProfileManager.getUsableNodes(
                softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)
