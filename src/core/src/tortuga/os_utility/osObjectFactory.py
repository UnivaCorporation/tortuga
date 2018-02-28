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

# pylint: disable=no-self-use

import sys
import logging
from tortuga.exceptions.abstractMethod import AbstractMethod
from tortuga.exceptions.invalidApplicationModule \
    import InvalidApplicationModule


class OsObjectFactory(object):
    """
    Base os object factory class.
    """

    def __init__(self):
        self._logger = logging.getLogger(
            'tortuga.osObjectFactory.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

    def getLogger(self):
        """ Get logger for this class. """
        return self._logger

    # Factory hooks.
    def getOsFamily(self):
        """ Get repository. """
        raise AbstractMethod(
            'getOsFamily() has to be overriden in the derived class.')

    def getRepo(self, osInfo, localPath, remoteUrl=None): \
            # pylint: disable=unused-argument
        """ Get repository. """
        raise AbstractMethod(
            'getRepo() has to be overriden in the derived class.')

    def getPackage(self, uri): \
            # pylint: disable=unused-argument
        """ Get package. """
        raise AbstractMethod(
            'getPackage() has to be overriden in the derived class.')

    def getOsServiceManager(self):
        """ Get OS service manager. """
        raise AbstractMethod(
            'getOsServiceManager() has to be overriden in the derived class.')

    def getOsApplicationManager(self, applicationName,
                                tortugaDir='os_objects'):
        """ Get OS application manager. """

        try:
            osFamily = self.getOsFamily().lower()

            mgrClass = '%s%sManager' % (
                osFamily.capitalize(),
                applicationName.lower().capitalize())

            moduleName = 'tortuga.%s.%s.%s%sManager' % (
                tortugaDir, osFamily, osFamily,
                applicationName.lower().capitalize())

            module = __import__(moduleName)

            d = module.__dict__
            for m in moduleName.split('.')[1:]:
                d = d[m].__dict__

            cls = d[mgrClass]

            return cls()
        except Exception as ex:
            self._logger.error(ex)
            raise InvalidApplicationModule(
                'Invalid application module for: %s (Error: %s)' % (
                    applicationName, ex))

    def getOsKitApplicationManager(self, applicationName, dirPath=None):
        """ Get OS kit application manager. """

        try:
            if dirPath:
                sys.path = [dirPath] + sys.path

            osFamily = self.getOsFamily().lower()

            mgrClass = '%sManager' % (applicationName.lower().capitalize())

            moduleName = '%sManager' % (applicationName.lower())

            _temp = __import__(
                '%s.%s' % (osFamily, moduleName), globals(), locals(),
                [mgrClass], 0)

            cls = getattr(_temp, mgrClass)

            if dirPath:
                del sys.path[0]

            return cls()
        except Exception as ex:
            self._logger.error(ex)
            raise InvalidApplicationModule(
                'Invalid application module for: %s (Error: %s)' % (
                    applicationName, ex))

    def getOsPackageManager(self):
        """ Get manager for package operations """
        raise AbstractMethod(
            'getOsPackageManager() has to be overriden in the derived'
            ' class.')

    def getOsFileSystemManager(self):
        """ Get manager for file system operations """
        raise AbstractMethod(
            'getOsFileSystemManager() has to be overriden in the derived'
            ' class.')

    def getOsNetworkManager(self):
        """ Get manager for networkoperations """
        raise AbstractMethod(
            'getOsNetworkManager() has to be overriden in the derived'
            ' class.')

    def getOsSysManager(self):
        """ Get manager for system """
        raise AbstractMethod(
            'getOsSysManager() has to be overriden in the derived class.')

    def getComponentManager(self):
        """Get manager for components"""
        raise AbstractMethod(
            'getComponentManager() has to be overriden in the derived'
            ' class.')

    def getOsBootHostManager(self):
        """Get manager for boothost"""
        raise AbstractMethod(
            'getOsBootHostManager() has to be overridden in the derived'
            ' class.')

    def getOsAddHostManager(self):
        """Get manager for addhost"""
        raise AbstractMethod(
            'getOsAddHostManager() has to be overridden in the derived'
            ' class.')

    def getTortugawsManager(self):
        """Get manager for tortugaws"""
        raise AbstractMethod(
            'getTortugawsManager() has to be overridden in the derived'
            ' class.')
