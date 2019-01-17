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

from tortuga.config.configManager import ConfigManager
from tortuga.objects.yumRepo import YumRepo
from tortuga.os_objects.rhel.rhelPackageManager import RhelPackageManager
from tortuga.os_objects.rhel.rhelServiceManager import RhelServiceManager
from tortuga.os_utility.osObjectFactory import OsObjectFactory


class RhelObjectFactory(OsObjectFactory):
    """
    RHEL object factory class
    """

    OS_FAMILY = 'rhel'

    # Factory hooks.
    def getOsFamily(self):
        return RhelObjectFactory.OS_FAMILY

    def getRepo(self, osInfo, localPath, remoteUrl=None):
        return YumRepo(osInfo, localPath, remoteUrl)

    def getPackageParser(self):
        from tortuga.package.rpm import RPM
        return RPM()

    def getOsServiceManager(self):
        return RhelServiceManager()

    def getOsPackageManager(self):
        return RhelPackageManager()

    def getOsFileSystemManager(self):
        from tortuga.os_objects.rhel.fileSystemManager import FileSystemManager
        return FileSystemManager()

    def getOsNetworkManager(self):
        from tortuga.os_objects.rhel.networkManager import NetworkManager
        return NetworkManager()

    def getOsSysManager(self):
        from tortuga.os_objects.rhel.sysManager import SysManager
        return SysManager()

    def getComponentManager(self):
        from tortuga.os_objects.rhel.componentManager import ComponentManager
        return ComponentManager()

    def getOsBootHostManager(self, configManager: ConfigManager):
        from tortuga.os_objects.rhel.bootHostManager import BootHostManager
        return BootHostManager(configManager)

    def getTortugawsManager(self):
        from tortuga.os_objects.rhel.tortugawsManager import TortugawsManager
        return TortugawsManager()
