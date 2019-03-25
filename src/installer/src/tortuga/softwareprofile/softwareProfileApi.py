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
import logging

from sqlalchemy.orm.session import Session

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.logging import SOFTWARE_PROFILE_NAMESPACE
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.softwareprofile.softwareProfileManager import \
    SoftwareProfileManager
from tortuga.utility.tortugaApi import TortugaApi


class SoftwareProfileApi(TortugaApi): \
        # pylint: disable=too-many-public-methods
    """
    SoftwareProfile API class.
    """

    def __init__(self):
        super(SoftwareProfileApi, self).__init__()

        self._softwareProfileManager = SoftwareProfileManager()
        self._logger = logging.getLogger(SOFTWARE_PROFILE_NAMESPACE)

    def getSoftwareProfile(self, session: Session, softwareProfileName,
                           optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.getSoftwareProfile(
                session, softwareProfileName, optionDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getSoftwareProfileById(self, session: Session, softwareProfileId,
                               optionDict=None):
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.getSoftwareProfileById(
                session, softwareProfileId, optionDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def deleteSoftwareProfile(self, session: Session, softwareProfileName):
        """
        Delete the specified software profile

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            self._softwareProfileManager.deleteSoftwareProfile(
                session, softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getSoftwareProfileList(self, session: Session, tags=None):
        """
        Returns a list of all software profiles.
        """
        try:
            return self._softwareProfileManager.getSoftwareProfileList(
                session, tags=tags)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getEnabledComponentList(self, session: Session, name):
        """
        Get enabled component list..

            Returns:
                list of enabled components
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.getEnabledComponentList(
                session, name)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getPartitionList(self, session: Session, softwareProfileName):
        """
        Get partition list for a given softwareprofile

            Returns:
                [partition]
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        try:
            return self._softwareProfileManager.getPartitionList(
                session, softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def addUsableHardwareProfileToSoftwareProfile(
            self, session: Session, hardwareProfileName: str,
            softwareProfileName: str) -> None:
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
            self._softwareProfileManager.addUsableHardwareProfileToSoftwareProfile(
                session, hardwareProfileName, softwareProfileName)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                       session: Session,
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
            self._softwareProfileManager.deleteUsableHardwareProfileFromSoftwareProfile(
                session, hardwareProfileName, softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def addAdmin(self, session: Session, softwareProfileName, adminUsername):
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
            self._softwareProfileManager.addAdmin(session, softwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def deleteAdmin(self, session: Session, softwareProfileName, adminUsername):
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
            self._softwareProfileManager.deleteAdmin(
                session, softwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def updateSoftwareProfile(self, session: Session, softwareProfileObject):
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
            self._softwareProfileManager.updateSoftwareProfile(
                session, softwareProfileObject)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def createSoftwareProfile(self, session: Session, swProfileSpec,
                              settingsDict=None):
        try:
            self._softwareProfileManager.createSoftwareProfile(
                session, swProfileSpec, settingsDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getNodeList(self, session: Session, softwareProfileName):
        try:
            return self._softwareProfileManager.getNodeList(
                session,
                softwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def enableComponent(self, session: Session, softwareProfileName, kitName,
                        kitVersion,
                        kitIteration, compName, compVersion=None):
        try:
            return self._softwareProfileManager.enableComponent(
                session,
                softwareProfileName,
                kitName,
                kitVersion,
                kitIteration,
                compName,
                compVersion,
            )
        except Exception as ex:
            if not isinstance(ex, TortugaException):
                self._logger.exception(
                    'Exception raised in {0}.enableComponent()'.format(
                        self.__class__.__name__))

                # Wrap exception
                raise TortugaException(exception=ex)

            raise

    def disableComponent(self, session: Session, softwareProfileName, kitName,
                         kitVersion, kitIteration, compName, compVersion=None):
        try:
            return self._softwareProfileManager.disableComponent(
                session,
                softwareProfileName,
                kitName,
                kitVersion,
                kitIteration,
                compName,
                compVersion,
            )
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def copySoftwareProfile(self, session: Session, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        try:
            return self._softwareProfileManager.copySoftwareProfile(
                session, srcSoftwareProfileName, dstSoftwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getUsableNodes(self, session: Session, softwareProfileName: str) \
            -> TortugaObjectList:
        try:
            return self._softwareProfileManager.getUsableNodes(
                session, softwareProfileName)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)
