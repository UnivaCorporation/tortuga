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
import tortuga.objects.osFamilyInfo


class OsInfo(TortugaObject): \
        # pylint: disable=too-many-public-methods

    """
    This class keeps OS information.
    """
    ROOT_TAG = 'os'

    def __init__(self, name=None, version=None, arch=None):
        TortugaObject.__init__(self, {
            'name': name,
            'version': version,
            'arch': arch
        }, ['name', 'version', 'arch', 'id'], OsInfo.ROOT_TAG)

    def setName(self, name):
        """ Set OS name. """
        self['name'] = name

    def getName(self):
        """ Return OS name. """
        return self.get('name')

    def setVersion(self, version):
        """ Set OS version. """
        self['version'] = version

    def getVersion(self):
        """ Return OS version. """
        return self.get('version')

    def setArch(self, arch):
        """ Set OS arch. """
        self['arch'] = arch

    def getArch(self):
        """ Return OS architecture. """
        return self.get('arch')

    def setId(self, id_):
        """ Set id."""
        self['id'] = id_

    def getId(self):
        """ Return id. """
        return self.get('id')

    def getOsFamilyInfo(self):
        """ Return the osFamily """
        return self.get('osFamily')

    def setOsFamilyInfo(self, osFamily):
        """ Set the os family for this object """
        self['osFamily'] = osFamily

    def __repr__(self):
        return '%s-%s-%s' % (self.getName(), self.getVersion(), self.getArch())

    def __eq__(self, other):
        if not self.getOsFamilyInfo() and other.getOsFamilyInfo():
            return False
        elif self.getOsFamilyInfo() and not other.getOsFamilyInfo():
            return False

        # Ensure all fields match and either osFamilyInfo is undefined or
        # matching 'other'
        return self.getName() == other.getName() and \
            self.getVersion() == other.getVersion() and \
            self.getArch() == other.getArch() and \
            (not self.getOsFamilyInfo() or
             (self.getOsFamilyInfo() == other.getOsFamilyInfo()))

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def getKeys():
        return ['id', 'name', 'version', 'arch']

    @classmethod
    def getFromDict(cls, _dict):
        """ Get os info from dict. """

        osInfo = super(OsInfo, cls).getFromDict(_dict)

        osFamilyDict = _dict.get(
            tortuga.objects.osFamilyInfo.OsFamilyInfo.ROOT_TAG)

        if osFamilyDict:
            osInfo.setOsFamilyInfo(
                tortuga.objects.osFamilyInfo.OsFamilyInfo.getFromDict(
                    osFamilyDict))

        return osInfo

    @classmethod
    def getFromDbDict(cls, _dict):
        osInfo = super(OsInfo, cls).getFromDict(_dict)

        osFamilyDict = _dict.get(
            tortuga.objects.osFamilyInfo.OsFamilyInfo.ROOT_TAG)

        if osFamilyDict:
            osInfo.setOsFamilyInfo(
                tortuga.objects.osFamilyInfo.OsFamilyInfo.getFromDbDict(
                    osFamilyDict.__dict__))

        return osInfo
