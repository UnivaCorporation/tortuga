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
from tortuga.objects.tortugaObject import TortugaObjectList
import tortuga.objects.kit
import tortuga.objects.osInfo
import tortuga.objects.osFamilyInfo
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.osComponent import OsComponent
from tortuga.objects.osFamilyComponent import OsFamilyComponent


class Component(TortugaObject): \
        # pylint: disable=too-many-public-methods
    """
    Component class.
    """

    ROOT_TAG = 'component'

    def __init__(self, name=None, version=None):
        TortugaObject.__init__(self, {
            'name': name,
            'version': version,
            'packageList': TortugaObjectList(),
            'osComponentList': TortugaObjectList(),
            'osFamilyComponentList': TortugaObjectList()
        }, ['name', 'version', 'id'], Component.ROOT_TAG)

    def __repr__(self):
        return '%s-%s' % (self.getName(), self.getVersion())

    def getName(self):
        """ Return component name. """
        return self.get('name')

    def addOsInfo(self, osInfo):
        """
        Associate an operating system to the component.  Initialize all
        related properties for this operating system
        """
        osComponentList = self.getOsComponentList()
        osComponent = OsComponent(osInfo)
        osComponentList.append(osComponent)
        return osComponent

    def addOsFamilyInfo(self, osFamilyInfo):
        """
        Associate an operating system family to this component.  Initialize
        all related properties for this operating system family
        """
        osFamilyComponentList = self.getOsFamilyComponentList()
        osFamilyComponent = OsFamilyComponent(osFamilyInfo)
        osFamilyComponentList.append(osFamilyComponent)
        return osFamilyComponent

    def getVersion(self):
        """ Return component version. """
        return self.get('version')

    def setId(self, id_):
        """ Set id."""
        self['id'] = id_

    def getId(self):
        """ Return id. """
        return self.get('id')

    def setDescription(self, description):
        """ Set component description. """
        self['description'] = description

    def getDescription(self):
        """ Get component description. """
        return self.get('description')

    def setIntegrationModulePath(self, modulePath):
        """ Set integration module path. """
        self['integrationModulePath'] = modulePath

    def getIntegrationModulePath(self):
        """ Get integration module path. """
        return self.get('integrationModulePath')

    def getOsComponentList(self):
        return self['osComponentList']

    def setOsComponentList(self, osComponentList):
        self['osComponentList'] = osComponentList

    def getOsFamilyComponentList(self):
        return self['osFamilyComponentList']

    def setOsFamilyComponentList(self, osFamilyComponentList):
        self['osFamilyComponentList'] = osFamilyComponentList

    def getOsInfoList(self):
        """ Get OS info. """
        osInfoList = TortugaObjectList()
        for osComponent in self.getOsComponentList():
            osInfoList.append(osComponent.getOsInfo())
        return osInfoList

    def getOsFamilyInfoList(self):
        """Get OS family info"""
        osInfoList = TortugaObjectList()
        for osFamilyComponent in self.getOsFamilyComponentList():
            osInfoList.append(osFamilyComponent.getOsFamilyInfo())
        return osInfoList

    def setKit(self, kit):
        """ Set kit info. """
        self['kit'] = kit

    def getKit(self):
        """ Get Kit. """
        return self.get('kit')

    def addPackage(self, package):
        """ Add package. """
        self['packageList'].append(package)

    def getPackageList(self):
        """ Get package list. """
        return self.get('packageList')

    def getOsComponent(self, osInfo):
        for osComponent in self.getOsComponentList():
            if osComponent.getOsInfo() == osInfo:
                return osComponent
        return None

    def getOsFamilyComponent(self, osFamilyInfo):
        for osFamilyComponent in self.getOsFamilyComponentList():
            if osFamilyComponent.getOsFamilyInfo() == osFamilyInfo:
                return osFamilyComponent
        return None

    def getComponentRepoDir(self):
        """ Get kit repo directory. """
        k = self.getKit()
        if k:
            if k.getIsOs():
                osname, osver, osarch = self.getName().split('-')
                return '%s/%s/%s' % (osname, osver, osarch)
            else:
                return '%s/%s/noarch' % (k.getName(), k.getDbVersion())
        raise TortugaException(
            "Not enough information in component to determine Repo Dir")

    def getYumRepoPath(self):
        return "/tortuga/repos/%s" % self.getComponentRepoDir()

    @staticmethod
    def getKeys():
        return [
            'name', 'version', 'description', 'integrationModulePath',
            'id'
        ]

    @classmethod
    def getFromDict(cls, _dict):
        """ Get component from _dict. """

        component = super(Component, cls).getFromDict(_dict)

        # Check if component has an operating system relation or an
        # operating system family relation

        component.setOsComponentList(OsComponent.getListFromDict(_dict))

        component.setOsFamilyComponentList(
            OsFamilyComponent.getListFromDict(_dict))

        kitDict = _dict.get(tortuga.objects.kit.Kit.ROOT_TAG)

        if kitDict:
            component.setKit(tortuga.objects.kit.Kit.getFromDict(kitDict))

        return component

    @classmethod
    def getFromDbDict(cls, _dict):
        component = super(Component, cls).getFromDict(_dict)

        component.setOsComponentList(OsComponent.getListFromDbDict(_dict))

        component.setOsFamilyComponentList(
            OsFamilyComponent.getListFromDbDict(_dict))

        kitDict = _dict.get(tortuga.objects.kit.Kit.ROOT_TAG)

        if kitDict:
            component.setKit(
                tortuga.objects.kit.Kit.getFromDbDict(kitDict.__dict__))

        return component
