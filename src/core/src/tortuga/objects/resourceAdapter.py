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

from tortuga.objects.tortugaObject import TortugaObject


class ResourceAdapter(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'resourceadapter'

    def __init__(self, name=None, kitId=None):
        TortugaObject.__init__(self, {
            'name': name,
            'kitId': kitId}, ['id', 'name'], ResourceAdapter.ROOT_TAG)

    def __repr__(self):
        return self.getName()

    def getId(self):
        return self['id']

    def setId(self, id_):
        self['id'] = id_

    def getName(self):
        return self['name']

    def setName(self, name):
        self['name'] = name

    def getKitId(self):
        return self['kitId']

    def setKitId(self, kitId):
        self['kitId'] = kitId

    @staticmethod
    def getKeys():
        return ['id', 'name', 'kitId']
