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

import configparser
import logging
import os

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.objects.osInfo import OsInfo
from tortuga.os_utility import osUtility


class RepoManager:
    """
    Class for repository management.
    """

    def __init__(self):
        """ Initialize repository manager instance. """
        self._logger = logging.getLogger(
            'tortuga.%s' % (self.__class__.__name__))
        self._kitArchiveDir = None
        self._cm = ConfigManager()
        self._repoRoot = self._cm.getReposDir()
        self._repoMap = {}
        self.__configure()

    def __configureRepo(self, osInfo, localPath, remoteUrl=None): \
            # pylint: disable=unused-argument
        """ Configure repo for a given OS"""
        repo = None
        osName = osInfo.getName()
        factoryModule = '%sObjectFactory' % osName
        factoryClass = '%sObjectFactory' % osName.capitalize()

        _temp = __import__('tortuga.os_utility.{0}'.format(factoryModule),
                           globals(),
                           locals(),
                           [factoryClass],
                           0)

        Factory = getattr(_temp, factoryClass)

        repo = Factory().getRepo(osInfo, localPath, remoteUrl)

        repo.createRoot()

        self._logger.debug('Configured repo [%s] for [%s]' % (repo, osInfo))

        return repo

    def __configure(self):
        """ Configure all repositories from the config file. """

        self._kitArchiveDir = self._cm.getKitDir()
        configFile = self._cm.getRepoConfigFile()

        if not os.path.exists(configFile):
            self._logger.debug(
                'Repo configuration file [%s] not found' % (configFile))
        else:
            self._logger.debug(
                'Reading repo configuration file [%s]' % (configFile))

        configParser = configparser.ConfigParser()
        configParser.read(configFile)

        try:
            osKeyList = configParser.sections()

            if osKeyList:
                self._logger.debug(
                    'Found OS sections [%s]' % (' '.join(osKeyList)))

            for osKey in osKeyList:
                self._logger.debug('Parsing OS section [%s]' % (osKey))

                osData = osKey.split('__')
                osName = osData[0]
                osVersion = osData[1]
                osArch = osData[2]
                osInfo = OsInfo(osName, osVersion, osArch)

                # Ignore all repos that weren't enabled
                bEnabled = True
                if configParser.has_option(osKey, 'enabled'):
                    value = configParser.get(osKey, 'enabled')
                    bEnabled = value.lower() == 'true'

                if not bEnabled:
                    self._logger.debug('Repo for [%s] is disabled' % (osInfo))

                    continue

                localPath = None
                if configParser.has_option(osKey, 'localPath'):
                    localPath = configParser.get(osKey, 'localPath', True)

                if not localPath:
                    localPath = self._repoRoot

                remoteUrl = None
                if configParser.has_option(osKey, 'remoteUrl'):
                    remoteUrl = configParser.get(osKey, 'remoteUrl', True)

                repo = self.__configureRepo(osInfo, localPath, remoteUrl)

                self._repoMap[osKey] = repo

            if not os.path.exists(self._kitArchiveDir):
                self._logger.debug(
                    'Creating kit archive directory [%s]' % (
                        self._kitArchiveDir))

                os.makedirs(self._kitArchiveDir)

            osInfo = osUtility.getNativeOsInfo()

            repo = self.__configureRepo(osInfo, self._repoRoot)

            osKey = '%s__%s__%s' % (
                osInfo.getName(), osInfo.getVersion(), osInfo.getArch())

            # Configure repo for native os if there are no repos configured.
            if osKey not in self._repoMap:
                self._repoMap[osKey] = repo
        except ConfigurationError:
            raise
        except Exception as ex:
            raise ConfigurationError(exception=ex)

    def getRepo(self, osInfo=None):
        """ Return repo given os info. """

        if not osInfo:
            osInfo = osUtility.getNativeOsInfo()

        osKey = '%s__%s__%s' % (
            osInfo.getName(), osInfo.getVersion(), osInfo.getArch())

        return self._repoMap.get(osKey)

    def getRepoList(self):
        """ Return all repos. """
        return list(self._repoMap.values())

    def getKitArchiveDir(self):
        """ Return kit archive directory. """
        return self._kitArchiveDir


def getRepo(osInfo=None):
    """ Return repo given os info. """
    return RepoManager().getRepo(osInfo)


def getRepoList():
    """ Return repo list. """
    return RepoManager().getRepoList()


def getKitArchiveDir():
    """ Return kit archive directory. """
    return RepoManager().getKitArchiveDir()
