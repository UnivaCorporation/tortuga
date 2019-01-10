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
from typing import Optional

from sqlalchemy.orm.session import Session
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.hardwareprofile.hardwareProfileManager import \
    HardwareProfileManager
from tortuga.logging import HARDWARE_PROFILE_NAMESPACE
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.utility.tortugaApi import TortugaApi


class HardwareProfileApi(TortugaApi):
    """
    HardwareProfile API class.
    """
    
    def __init__(self):
        super().__init__()
        
        self._logger = logging.getLogger(HARDWARE_PROFILE_NAMESPACE)

    def getHardwareProfile(self, session: Session, hardwareProfileName,
                           optionDict=None):
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().getHardwareProfile(
                session, hardwareProfileName, optionDict or {})
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getHardwareProfileById(self, session: Session, id_, optionDict=None):
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().getHardwareProfileById(
                session, id_, optionDict or {})
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteHardwareProfile(self, session: Session, hardwareProfileName):
        """
        Delete hardware profile

            Returns:
                N/A
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            HardwareProfileManager().deleteHardwareProfile(
                session, hardwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getHardwareProfileList(self, session: Session, optionDict=None,
                               tags=None):
        """
        Get list of hardware profiles

            Returns:
                [hardwareProfile]
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().getHardwareProfileList(
                session, optionDict=optionDict, tags=tags)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def addAdmin(self, session: Session, hardwareProfileName, adminUsername):
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """
        try:
            HardwareProfileManager().addAdmin(
                session, hardwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteAdmin(self, session: Session, hardwareProfileName,
                    adminUsername):
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """
        try:
            HardwareProfileManager().deleteAdmin(
                session, hardwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def updateHardwareProfile(self, session: Session, hardwareProfileObject):
        """
        Update a hardware profile in the database that matches the passed
        in hardware profile object.  The ID is used as the primary
        matching criteria.

            Returns:
                None
            Throws:
                TortugaException
                HardwareProfileNotFound

        """
        try:
            HardwareProfileManager().updateHardwareProfile(
                session,
                hardwareProfileObject)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def createHardwareProfile(self, session: Session,
                              hwProfileSpec: HardwareProfile,
                              settingsDict: Optional[dict] = None) \
            -> None:
        """
        Create hardware profile from template

            Returns:
                None
            Throws:
                TortugaException
        """
        try:
            HardwareProfileManager().createHardwareProfile(
                session, hwProfileSpec, settingsDict=settingsDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def setProvisioningNic(self, session: Session, hardwareProfileName, nicId):
        """
        Mark nic as a provisioning interface in the specified hardware profile

        Throws:
            TortugaException
            HardwareProfileNotFound
        """
        try:
            HardwareProfileManager().setProvisioningNic(
                session, hardwareProfileName, nicId)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getProvisioningNicForNetwork(self, session: Session, network, netmask):
        try:
            HardwareProfileManager().getProvisioningNicForNetwork(
                session, network, netmask)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def copyHardwareProfile(self, session: Session, srcHardwareProfileName,
                            dstHardwareProfileName):
        try:
            return HardwareProfileManager().copyHardwareProfile(
                session, srcHardwareProfileName, dstHardwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def setIdleSoftwareProfile(self, session: Session, hardware_profile_name,
                               software_profile_name=None):
        try:
            HardwareProfileManager().setIdleSoftwareProfile(
                session, hardware_profile_name, software_profile_name)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getNodeList(self, session: Session, hardware_profile_name):
        try:
            HardwareProfileManager().getNodeList(
                session, hardware_profile_name)
        except TortugaException as exc:
            raise
        except Exception as exc:
            self._logger.exception('%s' % (exc))
            raise TortugaException(exception=exc)
