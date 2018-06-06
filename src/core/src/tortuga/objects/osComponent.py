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

from typing import Iterable, Optional

from tortuga.objects.osInfo import OsInfo
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList


class OsComponent(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'os_component'

    def __init__(self, osInfo=None):
        TortugaObject.__init__(self, {
            'osInfo': osInfo,
            'requires': TortugaObjectList(),
        }, [], OsComponent.ROOT_TAG)

    def setOsInfo(self, osInfo):
        self['osInfo'] = osInfo

    def getOsInfo(self):
        return self['osInfo']

    @classmethod
    def getFromDict(cls, dict_, ignore: Optional[Iterable[str]] = None):
        osDict = dict.get(OsInfo.ROOT_TAG)
        osInfo = OsInfo.getFromDict(osDict)

        osComponent = super(OsComponent, cls).getFromDict(dict_)

        osComponent.setOsInfo(osInfo)

        return osComponent

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        osDict = _dict.get(OsInfo.ROOT_TAG)
        osInfo = OsInfo.getFromDbDict(osDict.__dict__, ignore=ignore)

        osComponent = super(OsComponent, cls).getFromDict(_dict)

        osComponent.setOsInfo(osInfo)

        return osComponent
