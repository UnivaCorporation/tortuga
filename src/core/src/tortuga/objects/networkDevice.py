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


class NetworkDevice(TortugaObject): \
        # pylint: disable=too-many-public-methods

    """
    This class is used to describe parameters.
    """

    ROOT_TAG = 'networkdevice'

    def __init__(self, name=None):
        TortugaObject.__init__(
            self, {'name': name}, ['name'], NetworkDevice.ROOT_TAG)

    def setName(self, name):
        """ Set name."""
        self['name'] = name

    def getName(self):
        """ Return name. """
        return self.get('name')

    def setId(self, id_):
        """ Set id."""
        self['id'] = id_

    def getId(self):
        """ Return id. """
        return self.get('id')

    def __repr__(self):
        """ Display info. """
        return self.getName()

    @staticmethod
    def getKeys():
        return ['id', 'name']
