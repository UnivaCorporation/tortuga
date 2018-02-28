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

import os

from tortuga.objects.tortugaObject import TortugaObject


class Repo(TortugaObject): \
        # pylint: disable=too-many-public-methods

    """
    Base repository class.
    """

    def __init__(self, osInfo, localPath, remoteUrl=None):
        """ Initialize repo. """
        TortugaObject.__init__(self, {
            'osInfo': osInfo,
            'localPath': localPath,
            'remoteUrl': remoteUrl,
        }, [], 'repo')

    def getOsInfo(self):
        """ Return OS info. """
        return self.get('osInfo')

    def getLocalPath(self):
        """ Return local path to the repository. """
        return self.get('localPath')

    def getRemoteUrl(self):
        """ Return URL for the remote repository. """
        return self.get('remoteUrl')

    def __repr__(self):
        """ Display info. """
        return self.get('localPath')

    def createRoot(self):
        """ Initialize root repository. """
        localPath = self['localPath']

        if not os.path.exists(localPath):
            os.makedirs(localPath)

    # Repo hooks. Derived repository should be smart enough to
    # recognize whether they are working on OS they can handle.
    def create(self, relativePath, cachedDir=None): \
            # pylint: disable=unused-argument
        pass

    def delete(self, relativePath): \
            # pylint: disable=unused-argument
        pass

    def addPackage(self, packagePath, relativePath): \
            # pylint: disable=unused-argument
        pass
