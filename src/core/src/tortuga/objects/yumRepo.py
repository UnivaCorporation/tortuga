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

import os
import shutil

from tortuga.objects.repo import Repo
from tortuga.os_utility import tortugaSubprocess
from tortuga.os_utility import osUtility


class YumRepo(Repo): \
        # pylint: disable=too-many-public-methods

    """
    Yum repository class.
    """

    def __init__(self, osConfig, localPath, remoteUrl=None):
        """ Initialize repo. """
        Repo.__init__(self, osConfig, localPath, remoteUrl)

    def __getRepoPath(self, relativePath):
        return os.path.join(self.getLocalPath(), relativePath)

    # Repo hooks.
    def create(self, relativePath, cacheDir=None):
        repoPath = self.__getRepoPath(relativePath)

        if not os.path.exists(repoPath):
            os.makedirs(repoPath)

        # Make sure nothing happens here for non-native os.
        if not osUtility.isNativeOsName(self.getOsInfo()):
            return

        # Build 'createrepo' command-line
        cmd = 'createrepo -q'
        if cacheDir is not None:
            cmd += ' --cachedir %s' % (cacheDir)
        cmd += ' %s' % (repoPath)

        tortugaSubprocess.executeCommand(cmd)

    def delete(self, relativePath):
        pass

    def addPackage(self, packagePath, relativePath):
        repoPath = self.__getRepoPath(relativePath)

        shutil.copy(packagePath, repoPath)

    def start(self, relativePath):
        pass

    def stop(self, relativePath):
        pass
