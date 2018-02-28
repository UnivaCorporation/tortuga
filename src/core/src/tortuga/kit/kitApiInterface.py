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


class KitApiInterface(object):
    """
    Kit API interface.
    """

    def getKit(self, name, version, iteration=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get kit info.

            Returns:
                kit
            Throws:
                KitNotFound
                TortugaException
        """
        raise AbstractMethod('getKit() has to be implemented in the'
                             ' concrete API class.')

    def getKitById(self, id_): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get kit info by kitId.

            Returns:
                kit
            Throws:
                KitNotFound
                TortugaException
        """
        raise AbstractMethod('getKitById() has to be implemented in the'
                             ' concrete API class.')

    def getKitList(self): \
            # pylint: disable=no-self-use
        """
        Get kit list.

            Returns:
                [kits]
            Throws:
                TortugaException
        """
        raise AbstractMethod('getKitList() has to be implemented in the'
                             ' concrete API class.')

    def installKit(self, name, version, iteration=None, key=None): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('installKit() has to be implemented in the'
                             ' concrete API class.')

    def installOsKit(self, osMediaUrl, **kwargs): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('installOsKit() has to be implemented in the'
                             ' concrete API class.')

    def installKitPackage(self, packageUrl, key=None): \
            # pylint: disable=no-self-use,unused-argument
        """
            Install kit package.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """
        raise AbstractMethod('installKitPackage() has to be implemented'
                             ' in the concrete API class.')

    def deleteKit(self, name, version, iteration=None, force=False): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete kit.

            Returns:
                None
            Throws:
                UserNotAuthorized
                KitNotFound
                KitInUse
                TortugaException
        """
        raise AbstractMethod('deleteKit() has to be implemented in the'
                             ' concrete API class.')

    def getKitEula(self, name, version, iteration=None): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('getKitEula() has to be implemented in the'
                             ' concrete API class.')

    def getKitPackageEula(self, packageUrl): \
            # pylint: disable=no-self-use,unused-argument
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
        raise AbstractMethod('getKitPackageEula() has to be implemented'
                             ' in the concrete API class.')
