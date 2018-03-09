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

from tortuga.db.componentDbApi import ComponentDbApi
from tortuga.helper import osHelper
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.os_objects.osObjectManager import OsObjectManager


class ComponentManager(OsObjectManager):
    def getBestMatchComponent(self, compName, compVersion, osInfo, kitId):
        return ComponentDbApi().getBestMatchComponent(
            compName, compVersion, osInfo, kitId)

    def _isMatchingMajorVersion(self, ver1, ver2):
        """Match major versions only"""
        return ver1.split('.')[0] == ver2.split('.')[0]

    def isCompatibleComponent(self, osInfo, component):
        osconfig = osHelper.getOsInfo(osInfo.getName(),
                                      osInfo.getVersion(),
                                      osInfo.getArch())

        for osComponent in component.getOsInfoList():
            if osComponent.getName() == osInfo.getName() and \
                self._isMatchingMajorVersion(osComponent.getVersion(),
                                             osInfo.getVersion()) and \
                    osComponent.getArch() == osInfo.getArch():
                return True

        for osFamilyComponent in component.getOsFamilyInfoList():
            if osFamilyComponent.getName() == 'root':
                return True

            if osFamilyComponent.getName() == osconfig.getOsFamilyInfo().\
                    getName():
                # Family matches
                if self._isMatchingMajorVersion(
                        osFamilyComponent.getVersion(),
                        osconfig.getOsFamilyInfo().getVersion()) or \
                        osFamilyComponent.getVersion is None:
                    # Version matches
                    if osFamilyComponent.getArch() == osconfig.getArch() or \
                            osFamilyComponent.getArch() is None:
                        # Arch matches
                        return True

        return False

    def getCompatibleComponentList(self, osInfo, componentList):
        return TortugaObjectList(
            [component for component in componentList
             if self.isCompatibleComponent(osInfo, component)])
