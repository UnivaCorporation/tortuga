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

from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList
import tortuga.objects.osFamilyInfo


class OsFamilyComponent(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'osfamily_component'

    def __init__(self, osFamilyInfo=None):
        TortugaObject.__init__(self, {
            'osFamilyInfo': osFamilyInfo,
            'requires': TortugaObjectList(),
        }, [], OsFamilyComponent.ROOT_TAG)

    def setOsFamilyInfo(self, osFamilyInfo):
        self['osFamilyInfo'] = osFamilyInfo

    def getOsFamilyInfo(self):
        return self['osFamilyInfo']

    @classmethod
    def getFromDict(cls, dict_):
        osFamilyDict = dict_.get(
            tortuga.objects.osFamilyInfo.OsFamilyInfo.ROOT_TAG)

        osFamilyInfo = tortuga.objects.osFamilyInfo.OsFamilyInfo.\
            getFromDict(osFamilyDict)

        osFamilyComponent = super(OsFamilyComponent, cls).getFromDict(dict_)
        osFamilyComponent.setOsFamilyInfo(osFamilyInfo)

        return osFamilyComponent

    @classmethod
    def getFromDbDict(cls, _dict):
        osFamilyInfoDict = _dict.get(
            tortuga.objects.osFamilyInfo.OsFamilyInfo.ROOT_TAG)

        osFamilyInfo = tortuga.objects.osFamilyInfo.OsFamilyInfo.\
            getFromDbDict(osFamilyInfoDict.__dict__)

        osFamilyComponent = super(OsFamilyComponent, cls).getFromDict(_dict)

        osFamilyComponent.setOsFamilyInfo(osFamilyInfo)

        return osFamilyComponent
