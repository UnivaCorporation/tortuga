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
import glob

from tortuga.os_objects.osPackageManagerInterface \
    import OsPackageManagerInterface
from tortuga.os_objects.osObjectManager import OsObjectManager
from tortuga.config.configManager import ConfigManager


class RhelPackageManager(OsObjectManager, OsPackageManagerInterface):
    """
    RHEL package manager.
    """

    def __init__(self):
        OsObjectManager.__init__(self)

        self._cm = ConfigManager()

    def buildPackageUrl(self, host, kitName, kitVersion, arch, isOs,
                        portNum=None):
        """
        Build up a URL based on some kit properties

            Returns:
                A url to a tortuga kit based on input
            Throws:
                None
        """

        # We need to get the mapping information if we have an os kit...
        # some dvds have subdirectories that contian the rpms
        additionalPath = None

        additionalRepoPaths = {
            'centos': "",
            'rhel': "/Server",
            'oracle': "/Server",
        }

        if isOs:
            additionalPath = additionalRepoPaths.get(kitName)

        if additionalPath is None:
            additionalPath = ""

        if not portNum:
            portNum = self._cm.getIntWebPort()

        return "http://%s:%s/repos/%s/%s/%s%s" % (
            host, portNum, kitName, kitVersion, arch, additionalPath)

    def removePackageSource(self, packageSourceName):
        """
        Remove package yum repo config file

            Returns:
                None
            Throws:
                CommandFailed
        """

        self.execute(
            '/bin/rm -f /etc/yum.repos.d/uc-kit-%s.repo' % (
                packageSourceName))

    def getPackageSourceNames(self):
        """
        Get list of package source names.

            Returns:
                [packageSourceNames]
        """

        packageSourceNames = []

        for repo in glob.glob('/etc/yum.repos.d/uc-kit-*.repo'):
            if os.path.isfile(repo):
                packageSourceName = os.path.basename(repo).\
                    replace('.repo', '').replace('uc-kit-', '')

                packageSourceNames.append(packageSourceName)

        return packageSourceNames
