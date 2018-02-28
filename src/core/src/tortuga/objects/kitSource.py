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

from tortuga.objects.tortugaObject import TortugaObject


class KitSource(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'kitsource'

    def __init__(self, url=None, description=None):
        TortugaObject.__init__(self, {
            'url': url,
            'description': description,
        }, ['name', 'description', 'id'], KitSource.ROOT_TAG)

    def getId(self):
        return self.get('id')

    def setId(self, id_):
        self['id'] = id_

    def getUrl(self):
        return self.get('url')

    def setUrl(self, url):
        self['url'] = url

    def getDescription(self):
        return self.get('description')

    def setDescription(self, description):
        self['description'] = description

    @staticmethod
    def getKeys():
        return ['id', 'url', 'description']
