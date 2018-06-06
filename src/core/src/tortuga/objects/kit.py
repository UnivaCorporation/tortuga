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

# pylint: disable=no-self-use,no-member

from typing import Iterable, Optional

import tortuga.objects.component
import tortuga.objects.kitSource
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList
from tortuga.utility.helper import str2bool


class Kit(TortugaObject): \
        # pylint: disable=too-many-public-methods
    """
    Base kit class.
    """

    ROOT_TAG = 'kit'

    def __init__(self, name=None, version=None, iteration=None):
        TortugaObject.__init__(self, {
            'name': name,
            'version': version,
            'iteration': iteration,
            'components': TortugaObjectList(),
            'sources': TortugaObjectList(),
        }, ['name', 'version', 'iteration', 'id'], Kit.ROOT_TAG)

    def setName(self, name):
        """ Set kit name."""
        self['name'] = name

    def getName(self):
        """ Return kit name. """
        return self.get('name')

    def setVersion(self, version):
        """ Set kit version."""
        self['version'] = version

    def getVersion(self):
        """ Return kit version. """
        return self.get('version')

    def setIteration(self, iteration):
        """ Set kit iteration."""
        self['iteration'] = iteration

    def getIteration(self):
        """ Return kit iteration. """
        return self.get('iteration')

    def setId(self, id_):
        """ Set id."""
        self['id'] = id_

    def getId(self):
        """ Return id. """
        return self.get('id')

    def setIsOs(self, isOs):
        """ Set isOs flag."""
        self['isOs'] = str2bool(isOs)

    def getIsOs(self):
        """ Return isOs flag. """
        return str2bool(self.get('isOs'))

    def setIsRemovable(self, isRemovable):
        """ Set isRemovable flag."""
        self['isRemovable'] = str2bool(isRemovable)

    def getIsRemovable(self):
        """ Return removable flag. """
        return str2bool(self.get('isRemovable'))

    def getFullName(self):
        """ Get full name. """
        return '%s-%s' % (self.getName(), self.getDbVersion())

    def setDocumentation(self, documentation):
        """ Set kit documentation."""
        self['documentation'] = documentation

    def getDocumentation(self):
        """ Return kit documentation. """
        return self.get('documentation')

    def getTarBz2FileName(self):
        """ Return .tar.bz2 file for this kit. """
        return 'kit-%s-%s.tar.bz2' % (self.get('name'), self.getDbVersion())

    def getDirName(self):
        """ Return unpacked directory name for this kit. """
        return 'kit-%s-%s' % (self.get('name'), self.getDbVersion())

    def getXmlFileName(self):
        """ Return xml file for this kit. """
        return 'kit.xml'

    def setDescription(self, description):
        """ Set kit description. """
        self['description'] = description

    def getDescription(self):
        """ Get kit description. """
        return self.get('description')

    def setIntegrationModulePath(self, modulePath):
        """ Set integration module path. """
        self['integrationModulePath'] = modulePath

    def getIntegrationModulePath(self):
        """ Get integration module path. """
        return self.get('integrationModulePath')

    def setOsInfo(self, osInfo):
        """ Set OS info. """
        self['osInfo'] = osInfo

    def getOsInfo(self):
        """ Get OS info. """
        return self.get('osInfo')

    def setKitId(self, kitId):
        """ Set kit id. """
        self['kitId'] = kitId

    def getKitId(self):
        """ Get kit id. """
        return self.get('kitId')

    def getEula(self):
        """ Return the path to the kit EULA file """
        return self.get('eula')

    def setEula(self, eula):
        """ Set the path to the kit EULA file """
        self['eula'] = eula

    def getKitRepoDir(self):
        """ Get kit repo directory. """
        return '%s/%s/noarch' % (self.getName(), self.getDbVersion())

    def getKitDocRootDir(self):
        """ Get the documentation root directory """
        from tortuga.config.configManager import ConfigManager
        docRoot = ConfigManager().getTortugaWebRoot() + '/docs'
        return '%s/%s-%s' % (docRoot, self.getName(), self.getDbVersion())

    def getDbVersion(self):
        """ Get version used in db. """
        if self.getIteration():
            return '%s-%s' % (self.getVersion(), self.getIteration())
        else:
            return '%s' % (self.getVersion())

    def addComponent(self, component):
        """ Add component. """
        self['components'].append(component)

    def setComponentList(self, componentList):
        self['components'] = componentList

    def getComponentList(self):
        """ Get component list for a given os. """
        return self['components']

    def getComponentListByNameVersion(self, name, version):
        """ Get component list for given name and version. """
        cList = []
        for c in self['components']:
            if c.getName() == name and c.getVersion() == version:
                cList.append(c)
        return cList

    def getUniqueOsInfoList(self):
        """ Get list of unique operating systems. """
        osInfoList = TortugaObjectList()
        for c in self['componentList']:
            isDuplicate = False
            for osInfo in osInfoList:
                if c.getOsInfo() == osInfo:
                    isDuplicate = True
                    break
            if not isDuplicate:
                osInfoList.append(c.getOsInfo())
        return osInfoList

    def setKitDir(self, kitDir):
        """ Set kit directory. """
        self['kitDir'] = kitDir

    def getKitDir(self):
        """ Get kit directory. """
        return self.get('kitDir')

    def setSpecFile(self, specFile):
        """ Set spec file. """
        self['specFile'] = specFile

    def getSpecFile(self):
        """ Get spec file. """
        return self.get('specFile')

    def getSources(self):
        return self.get('sources')

    def setSources(self, sources):
        self['sources'] = sources

    def __repr__(self):
        """ Get short display string. """
        return '%s-%s' % (self.getName(), self.getDbVersion())

    @staticmethod
    def getKeys():
        return [
            'name', 'version', 'iteration', 'description', 'id',
            'isRemovable', 'isOs']

    @classmethod
    def getFromDict(cls, dict_, ignore: Optional[Iterable[str]] = None):
        """ Get kit from dict. """

        kit = super(Kit, cls).getFromDict(dict_)

        kit.setComponentList(
            tortuga.objects.component.Component.getListFromDict(dict_))

        kit.setSources(
            tortuga.objects.kitSource.KitSource.getListFromDict(dict_))

        return kit

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        kit = super(Kit, cls).getFromDict(_dict)

        if not ignore or 'components' not in ignore:
            kit.setComponentList(
                tortuga.objects.component.Component.getListFromDbDict(
                    _dict, ignore=('kit',)))

        kit.setSources(
            tortuga.objects.kitSource.KitSource.getListFromDbDict(_dict))

        return kit
