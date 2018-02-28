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

from tortuga.objects.tortugaObject import TortugaObject, toBool


class Volume(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'volume'

    def __init__(self, volume_id=None, size=None, storageAdapter=None,
                 adapterVolume=None, persistent=False, shared=False):
        TortugaObject.__init__(self, {
            'id': volume_id,
            'size': size,
            'storageadapter': storageAdapter,
            'persistent': persistent,
            'adaptervolume': adapterVolume,
            'shared': shared
        }, ['id', 'storageadapter'], Volume.ROOT_TAG)

    def setId(self, val):
        self['id'] = val

    def getId(self):
        return self.get('id')

    def setSize(self, val):
        self['size'] = val

    def getSize(self):
        return self.get('size')

    def setAdapterVolume(self, val):
        self['adaptervolume'] = val

    def getAdapterVolume(self):
        return self.get('adaptervolume')

    def setStorageAdapter(self, val):
        self['storageadapter'] = val

    def getStorageAdapter(self):
        return self.get('storageadapter')

    def setPersistent(self, val):
        self['persistent'] = toBool(val)

    def getPersistent(self):
        return toBool(self.get('persistent'))

    def setShared(self, val):
        self['shared'] = toBool(val)

    def getShared(self):
        return toBool(self.get('shared'))

    @staticmethod
    def getKeys():
        return [
            'id', 'storageadapter', 'size', 'persistent', 'adaptervolume',
            'shared'
        ]
