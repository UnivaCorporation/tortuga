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


class SoftwareProfileApiInterface(object):
    """
    SoftwareProfile API interface.
    """

    def getSoftwareProfile(self, softwareProfileName, optionDict=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get software profile information

            Returns:
                softwareProfile
            Throws:
                TortugaException
        """
        raise AbstractMethod('getSoftwareProfile has to be implemented in'
                             ' the concrete API class.')

    def getSoftwareProfileById(self, softwareProfileId, optionDict=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get software profile information

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod('getSoftwareProfileById has to be implemented'
                             ' in the concrete API class.')

    def deleteSoftwareProfile(self, softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete software profile

            Returns:
                N/A
            Throws:
                TortugaException
        """
        raise AbstractMethod('deleteSoftwareProfile has to be'
                             ' implemented in the concrete API class.')

    def getSoftwareProfileList(self, tags=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Returns a list of all SoftwareProfile's in the system.
        """
        raise AbstractMethod('getSoftwareProfileList has to be implemented'
                             ' in the concrete API class.')

    def getIdleSoftwareProfileList(self): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get the list of idle software profiles

            Returns:
                The list of idle softwareprofiles
            Throws:
                TortugaException
        """
        raise AbstractMethod('getIdleSoftwareProfileList has to be'
                             ' implemented in the concrete API class.')

    def setIdleState(self, softwareProfileName, state): \
            # pylint: disable=no-self-use,unused-argument
        """
        Set the idle software profile state

            Returns:
                -none-
            Throws:
                TortugaException
        """
        raise AbstractMethod('setIdleState has to be implemented in the'
                             ' concrete API class.')

    def getEnabledComponentList(self, softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get the list of enabled components

            Returns:
                The list of enabled components for a softwareprofile
            Throws:
                TortugaException
        """
        raise AbstractMethod('getEnabledComponentList has to be'
                             ' implemented in the concrete API class.')

    def getPackageList(self, softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get the list of packages for a given softwareprofile

            Returns:
                [package]
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod('getPackageList has to be implemented in the'
                             ' concrete API class.')

    def getPartitionList(self, softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get the list of partitions for a given softwareprofile

            Returns:
                [partition]
            Throws:
                SoftwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod('getPartitionList has to be implemented in'
                             ' the concrete API class.')

    def addUsableHardwareProfileToSoftwareProfile(self,
                                                  hardwareProfileName,
                                                  softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Set useable hardware profile

            Returns:
                SoftwareUsesHardwareID
            Throws:
                SoftwareProfileNotFound
                HardwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod('addUsableHardwareProfileToSoftwareProfile'
                             ' has to be implemented in the concrete API'
                             ' class.')

    def deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                       hardwareProfileName,
                                                       softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete useable hardware profile

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                HardwareProfileNotFound
                TortugaException
        """
        raise AbstractMethod(
            'deleteUsableHardwareProfileFromSoftwareProfile has to be'
            ' implemented in the concrete API class.')

    def createSoftwareProfileFromTemplate(self, tmpl, tmplDict,
                                          osInfo=None,
                                          unmanagedProfile=False): \
            # pylint: disable=no-self-use,unused-argument
        """
        Create software profile from template

            Returns:
                None
            Throws:
                TortugaException
        """
        raise AbstractMethod('createSoftwareProfileFromTemplate has to'
                             ' be implemented in the concrete API class.')

    def addAdmin(self, softwareProfileName, adminUsername): \
            # pylint: disable=no-self-use,unused-argument
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """
        raise AbstractMethod('addAdmin() has to be implemented in the'
                             ' concrete API class.')

    def deleteAdmin(self, softwareProfileName, adminUsername): \
            # pylint: disable=no-self-use,unused-argument
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """
        raise AbstractMethod('deleteAdmin() has to be implemented in the'
                             ' concrete API class.')

    def updateSoftwareProfile(self, softwareProfileObject): \
            # pylint: disable=no-self-use,unused-argument
        """
        Update a software profile in the database that matches the
        passed in software profile object.  The ID is used as the primary
        matching criteria.

            Returns:
                None
            Throws:
                TortugaException
                SoftwareProfileNotFound
        """
        raise AbstractMethod('updateSoftwareProfile() has to be implemented'
                             ' in the concrete API class.')

    def enableComponent(self, softwareProfileName, kitName, kitVersion,
                        kitIteration, compName, compVersion): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('enableComponent() has to be implemented in'
                             ' the concrete API class.')

    def disableComponent(self, softwareProfileName, kitName, kitVersion,
                         kitIteration, compName, compVersion): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('disableComponent() has to be implemented'
                             ' in the concrete API class.')

    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Duplicate the specified software profile

            Returns:
                None
            Throws:
                TortugaException
                SoftwareProfileNotFound
                KitNotFound
                ComponentNotFound
        """
        raise AbstractMethod('copySoftwareProfile() has to be implemented'
                             ' in the concrete API class.')

    def getUsableNodes(self, softwareProfileName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Returns list of nodes with the same hardware profile as the
        specified software profile name
        """

        raise AbstractMethod(
            'getUsableNodes() has to be implemented in the concrete API'
            ' class.')
