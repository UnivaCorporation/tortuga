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


class OsFamilyInfo(TortugaObject): \
        # pylint: disable=too-many-public-methods

    """
    This class keeps OS information.
    """

    ROOT_TAG = 'family'

    def __init__(self, name=None, version=None, arch=None):
        TortugaObject.__init__(
            self, {'name': name, 'version': version, 'arch': arch},
            ['name', 'version', 'arch', 'id'], OsFamilyInfo.ROOT_TAG)

    def setName(self, name):
        """ Set OS family name"""
        self['name'] = name

    def getName(self):
        """ Return OS family name"""
        return self.get('name')

    def setVersion(self, version):
        """ Set OS family version"""
        self['version'] = version

    def getVersion(self):
        """ Return OS family version"""
        return self.get('version')

    def setArch(self, arch):
        """ Set OS family arch"""
        self['arch'] = arch

    def getArch(self):
        """ Return OS family architecture"""
        return self.get('arch')

    def setId(self, id_):
        """ Set id."""
        self['id'] = id_

    def getId(self):
        """ Return id. """
        return self.get('id')

    def __repr__(self):
        """ Display info. """
        return '%s-%s-%s' % (
            self.getName(), self.getVersion(), self.getArch())

    def __eq__(self, other):
        return self.getName() == other.getName() and \
            self.getVersion() == other.getVersion() and \
            self.getArch() == other.getArch()

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def getKeys():
        return ['id', 'name', 'version', 'arch']
