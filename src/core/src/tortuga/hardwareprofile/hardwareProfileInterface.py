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


class HardwareProfileApiInterface(object):
    """
    HardwareProfile API interface.
    """

    def getHardwareProfile(self, hardwareProfileName, optionDict=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                TortugaException
        """
        raise AbstractMethod('getHardwareProfile has to be implemented in'
                             ' the concrete API class.')

    def getHardwareProfileById(self, id_, optionDict=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get node group information

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod('getHardwareProfile has to be implemented in'
                             ' the concrete API class.')

    def deleteHardwareProfile(self, hardwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete hardware profile

            Returns:
                N/A
            Throws:
                TortugaException
        """
        raise AbstractMethod('deleteHardwareProfile has to be implemented'
                             ' in the concrete API class.')

    def getHardwareProfileList(self, optionDict=None, tags=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return list of hardware profiles
        """
        raise AbstractMethod('getHardwareProfileList has to be implemented'
                             ' in the concrete API class.')

    def updateSoftwareOverrideAllowed(self, hardwareProfileName, flag): \
            # pylint: disable=no-self-use,unused-argument
        raise AbstractMethod('updateSoftwareOverrideAllowed has to be'
                             ' implemented in the concrete API class.')

    def setIdleSoftwareProfile(self, hardwareProfileName,
                               softwareProfileName=None): \
            # pylint: disable=no-self-use,unused-argument
        '''Set the idle software profile'''
        raise AbstractMethod('setIdleSoftwareProfile has to be implemented'
                             ' in the concrete API class.')

    def getHypervisorNodes(self, hardwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        '''Get list of hypervisor nodes for a given hardare profile.'''
        raise AbstractMethod('getHypervisorNodes has to be implemented in'
                             ' the concrete API class.')

    def addAdmin(self, hardwareProfileName, adminUsername): \
            # pylint: disable=no-self-use,unused-argument
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """
        raise AbstractMethod('addAdmin() has to be implemented in the'
                             ' concrete API class.')

    def deleteAdmin(self, hardwareProfileName, adminUsername): \
            # pylint: disable=no-self-use,unused-argument
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """
        raise AbstractMethod('deleteAdmin() has to be implemented in the'
                             ' concrete API class.')

    def setProvisioningNic(self, hardwareProfileName, nicId): \
            # pylint: disable=no-self-use,unused-argument
        """
        Mark nic as a provisioning interface in the specified hardware
        profile

        Throws:
            TortugaException
            HardwareProfileNotFound
        """
        raise AbstractMethod('setProvisioningNic() has to be implemented'
                             ' in the concrete API class.')

    def updateHardwareProfile(self, hardwareProfileObject): \
            # pylint: disable=no-self-use,unused-argument
        """
        Update a hardware profile in the database that matches the passed
        in hardware profile object.  The ID is used as the primary matching
        criteria.

            Returns:
                None
            Throws:
                TortugaException
                HardwareProfileNotFound

        """
        raise AbstractMethod('updateHardwareProfile() has to be implemented'
                             ' in the concrete API class.')

    def createHardwareProfile(self, hwProfileSpec, settingsDict=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Create hardware profile from template

            Returns:
                None
            Throws:
                TortugaException
        """
        raise AbstractMethod('createrHardwareProfileFromTemplate() has to'
                             ' be implemented in the concrete API class.')

    def copyHardwareProfile(self, srcHardwareProfileName,
                            dstHardwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Duplicate the specified hardware profile

            Returns:
                None
            Throws:
                TortugaException
                HardwareProfileNotFound
                KitNotFound
                ComponentNotFound
        """
        raise AbstractMethod('copyHardwareProfile() has to be implemented'
                             ' in the concrete API class.')
