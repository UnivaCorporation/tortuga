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


class Package(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'package'

    def __init__(self, name=None):
        TortugaObject.__init__(
            self, {
                'name': name,
            }, ['name', 'softwareProfileId', 'id'], Package.ROOT_TAG)

    def setName(self, name):
        """ Set package name."""
        self['name'] = name

    def getName(self):
        """ Return package name. """
        return self.get('name')

    def setId(self, id_):
        """ Set package id."""
        self['id'] = id_

    def getId(self):
        """ Return package id. """
        return self.get('id')

    @staticmethod
    def getKeys():
        return ['id', 'name', 'softwareProfileId']
