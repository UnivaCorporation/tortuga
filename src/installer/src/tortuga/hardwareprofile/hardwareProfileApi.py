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

from typing import NoReturn, Optional, Union
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.hardwareprofile.hardwareProfileManager \
    import HardwareProfileManager
from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException


class HardwareProfileApi(TortugaApi):
    """
    HardwareProfile API class.
    """

    def getHardwareProfile(self, hardwareProfileName, optionDict=None):
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().\
                getHardwareProfile(hardwareProfileName, optionDict or {})
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getHardwareProfileById(self, id_, optionDict=None):
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().\
                getHardwareProfileById(id_, optionDict or {})
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def deleteHardwareProfile(self, hardwareProfileName):
        """
        Delete hardware profile

            Returns:
                N/A
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            HardwareProfileManager().\
                deleteHardwareProfile(hardwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getHardwareProfileList(self, optionDict=None, tags=None):
        """
        Get list of hardware profiles

            Returns:
                [hardwareProfile]
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        try:
            return HardwareProfileManager().\
                getHardwareProfileList(optionDict=optionDict,
                                       tags=tags)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            HardwareProfileManager().\
                addAdmin(hardwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
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
        try:
            HardwareProfileManager().\
                deleteAdmin(hardwareProfileName, adminUsername)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def updateHardwareProfile(self, hardwareProfileObject):
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
                hardwareProfileObject)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def createHardwareProfile(self, hwProfileSpec: HardwareProfile,
                              settingsDict: Optional[Union[dict, None]] = None) -> NoReturn:
        """
        Create hardware profile from template

            Returns:
                None
            Throws:
                TortugaException
        """
        try:
            HardwareProfileManager().createHardwareProfile(
                hwProfileSpec, settingsDict=settingsDict)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def setProvisioningNic(self, hardwareProfileName, nicId):
        """
        Mark nic as a provisioning interface in the specified hardware profile

        Throws:
            TortugaException
            HardwareProfileNotFound
        """
        try:
            HardwareProfileManager().setProvisioningNic(
                hardwareProfileName, nicId)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getProvisioningNicForNetwork(self, network, netmask):
        try:
            HardwareProfileManager().\
                getProvisioningNicForNetwork(network, netmask)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def copyHardwareProfile(self, srcHardwareProfileName,
                            dstHardwareProfileName):
        try:
            return HardwareProfileManager().\
                copyHardwareProfile(srcHardwareProfileName,
                                    dstHardwareProfileName)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def setIdleSoftwareProfile(self, hardware_profile_name,
                               software_profile_name=None):
        try:
            HardwareProfileManager().\
                setIdleSoftwareProfile(hardware_profile_name,
                                       software_profile_name)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def getNodeList(self, hardware_profile_name):
        try:
            HardwareProfileManager().getNodeList(
                hardware_profile_name)
        except TortugaException as exc:
            raise
        except Exception as exc:
            self.getLogger().exception('%s' % (exc))
            raise TortugaException(exception=exc)
