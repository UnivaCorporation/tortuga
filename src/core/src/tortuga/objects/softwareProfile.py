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

from functools import cmp_to_key
from typing import Iterable, Optional

import tortuga.objects.admin
import tortuga.objects.component
import tortuga.objects.hardwareProfile
import tortuga.objects.kitSource
import tortuga.objects.nic
import tortuga.objects.node
import tortuga.objects.osInfo
import tortuga.objects.partition
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList
from tortuga.utility.helper import str2bool


class SoftwareProfile(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'softwareprofile'

    def __init__(self, name=None):
        TortugaObject.__init__(
            self, {
                'name': name,
                'admins': TortugaObjectList(),
                'partitions': TortugaObjectList(),
                'components': TortugaObjectList(),
                'nodes': TortugaObjectList(),
                'kitsources': TortugaObjectList(),
            }, ['name', 'id'], SoftwareProfile.ROOT_TAG)

    def __repr__(self):
        return self.getName()

    def setId(self, id_):
        """ Set software profile id."""
        self['id'] = id_

    def getId(self):
        """ Return software profile id. """
        return self.get('id')

    def setName(self, name):
        """ Set software profile name."""
        self['name'] = name

    def getName(self):
        """ Return software profile name. """
        return self.get('name')

    def setDescription(self, description):
        """ Set description."""
        self['description'] = description

    def getDescription(self):
        """ Return description. """
        return self.get('description')

    def setKernel(self, kernel):
        """ Set kernel."""
        self['kernel'] = kernel

    def getKernel(self):
        """ Return kernel. """
        return self.get('kernel')

    def setKernelParams(self, kernelParams):
        """ Set kernel params."""
        self['kernelParams'] = kernelParams

    def getKernelParams(self):
        """ Return kernel params. """
        return self.get('kernelParams')

    def setInitrd(self, initrd):
        """ Set initrd."""
        self['initrd'] = initrd

    def getInitrd(self):
        """ Return initird. """
        return self.get('initrd')

    def setOsId(self, osId):
        """ Set OS id."""
        self['osId'] = osId

    def getOsId(self):
        """ Return OS id. """
        return self.get('osId')

    def setType(self, type_):
        """ Set type."""
        self['type'] = type_

    def getType(self):
        """ Return type. """
        return self.get('type')

    def setMinNodes(self, val):
        self['minNodes'] = val

    def getMinNodes(self):
        return self.get('minNodes')

    def setMaxNodes(self, value):
        self['maxNodes'] = value

    def getMaxNodes(self):
        return self.get('maxNodes')

    def setLockedState(self, val):
        self['lockedState'] = val

    def getLockedState(self):
        return self.get('lockedState')

    def setOsInfo(self, osInfo):
        """ Set OS info. """
        self['os'] = osInfo

    def getOsInfo(self):
        """ Get OS info. """
        return self.get('os')

    def setComponents(self, comp):
        """ Set components. """
        self['components'] = comp

    def getComponents(self):
        """ Get Components """
        return self.get('components')

    def setAdmins(self, admins):
        """ set Admins """
        self['admins'] = admins

    def getAdmins(self):
        """ Get Admins """
        return self.get('admins')

    def setPartitions(self, val):
        self['partitions'] = val

    def getPartitions(self):
        """ We want to always return the partitions sorted  by
            device and partition number """
        partitions = self.get('partitions')
        if partitions:
            partitions.sort(key=cmp_to_key(_partition_compare))
        return partitions

    def setNodes(self, val):
        self['nodes'] = val

    def getNodes(self):
        return self.get('nodes')

    def setIsIdle(self, val):
        self['isIdle'] = str2bool(val)

    def getIsIdle(self):
        return str2bool(self.get('isIdle'))

    def setUsableHardwareProfiles(self, val):
        self['hardwareprofiles'] = val

    def getUsableHardwareProfiles(self):
        return self.get('hardwareprofiles')

    def getKitSources(self):
        return self.get('kitsources')

    def setKitSources(self, kitsources):
        self['kitsources'] = kitsources

    def getTags(self):
        return self.get('tags')

    def setTags(self, tags):
        self['tags'] = tags

    def getMetadata(self):
        return self.get('metadata')

    def setMetadata(self, value):
        self['metadata'] = value

    def getDataRoot(self):
        return self.get('dataRoot')

    def setDataRoot(self, value):
        self['dataRoot'] = value

    @staticmethod
    def getKeys():
        return [
            'id',
            'name',
            'osId',
            'description',
            'kernel',
            'initrd',
            'kernelParams',
            'type',
            'minNodes',
            'maxNodes',
            'lockedState',
            'isIdle',
            'metadata',
            'tags',
            'dataRoot',
        ]

    @classmethod
    def getFromDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        """ Get software profile from _dict. """
        softwareProfile = super(SoftwareProfile, cls).getFromDict(_dict)
        softwareProfile.setAdmins(
            tortuga.objects.admin.Admin.getListFromDict(_dict))

        softwareProfile.setComponents(
            tortuga.objects.component.Component.getListFromDict(_dict))

        softwareProfile.setNodes(
            tortuga.objects.node.Node.getListFromDict(_dict))

        osDict = _dict.get(tortuga.objects.osInfo.OsInfo.ROOT_TAG)
        if osDict:
            softwareProfile.setOsInfo(
                tortuga.objects.osInfo.OsInfo.getFromDict(osDict))

        softwareProfile.setPartitions(
            tortuga.objects.partition.Partition.getListFromDict(_dict))

        softwareProfile.\
            setUsableHardwareProfiles(
                tortuga.objects.hardwareProfile.HardwareProfile.
                getListFromDict(_dict))

        # kitsources
        softwareProfile.setKitSources(
            tortuga.objects.kitSource.KitSource.getListFromDict(_dict))

        return softwareProfile

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        softwareProfile = super(SoftwareProfile, cls).getFromDict(
            _dict, ignore=ignore)

        softwareProfile.setAdmins(
            tortuga.objects.admin.Admin.getListFromDbDict(_dict))

        softwareProfile.setComponents(
            tortuga.objects.component.Component.getListFromDbDict(_dict))

        if not ignore or 'nodes' not in ignore:
            softwareProfile.setNodes(
                tortuga.objects.node.Node.getListFromDbDict(_dict))

        osDict = _dict.get(tortuga.objects.osInfo.OsInfo.ROOT_TAG)

        if osDict:
            softwareProfile.setOsInfo(
                tortuga.objects.osInfo.OsInfo.getFromDbDict(
                    osDict.__dict__))

        softwareProfile.setPartitions(
            tortuga.objects.partition.Partition.getListFromDbDict(_dict))

        softwareProfile.setUsableHardwareProfiles(
            tortuga.objects.hardwareProfile.HardwareProfile.
            getListFromDbDict(_dict))

        if 'tags' in _dict:
            tags = {}

            for tag in _dict['tags']:
                tags[tag.name] = tag.value

            softwareProfile.setTags(tags)

        return softwareProfile


def _partition_compare(x, y):
    deviceDiff = x.getDeviceTuple()[0] - y.getDeviceTuple()[0]

    if deviceDiff == 0:
        deviceDiff = x.getDeviceTuple()[1] - y.getDeviceTuple()[1]

    return deviceDiff
