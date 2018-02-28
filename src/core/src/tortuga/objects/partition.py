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

from tortuga.objects.tortugaObject import TortugaObject, toBool


class Partition(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'partition'

    def __init__(self, name=None, device=None):
        TortugaObject.__init__(self, {
            'name': name, 'device': device
        }, ['name', 'device', 'id'], Partition.ROOT_TAG)

    def setName(self, name):
        """ Set partition name."""
        self['name'] = name

    def getName(self):
        """ Return partition name. """
        return self.get('name')

    def setId(self, id_):
        """ Set partition id."""
        self['id'] = id_

    def getId(self):
        """ Return partition id. """
        return self.get('id')

    def getDeviceTuple(self):
        try:
            device = self.getDevice()
            device = device.split('.', 1)
            if len(device) == 1:
                device.append(0)
            device = (int(device[0]), int(device[1]))
        except Exception:
            from tortuga.exceptions.invalidPartitionScheme \
                import InvalidPartitionScheme

            raise InvalidPartitionScheme(
                'Invalid partition device name format')
        return device

    def setDevice(self, device):
        """ Set device."""
        self['device'] = device

    def getDevice(self):
        """ Return device. format is disknumber.parititon number
            not all install types support complete description.
            A '0' for either parameter indicates a "default" value."""
        return self.get('device')

    def setMountPoint(self, mountPoint):
        """ Set mount point."""
        self['mountPoint'] = mountPoint

    def getMountPoint(self):
        """ Return mount point tag. """
        return self.get('mountPoint')

    def setFsType(self, fsType):
        """ Set fs type."""
        self['fsType'] = fsType

    def getFsType(self):
        """ Return fs type. """
        return self.get('fsType')

    def setSize(self, size):
        """ Set size."""
        self['size'] = size

    def getSize(self):
        """ Return size. """
        return self.get('size')

    def setOptions(self, options):
        """ Set options."""
        self['options'] = options

    def getOptions(self):
        """ Return options. """
        return self.get('options')

    def setPreserve(self, preserve):
        """ Set preserve."""
        self['preserve'] = toBool(preserve)

    def getPreserve(self):
        """ Return preserve. """
        return toBool(self.get('preserve'))

    def setBootLoader(self, bootLoader):
        """ Set boot loader flag."""
        self['bootLoader'] = toBool(bootLoader)

    def getBootLoader(self):
        """ Return boot loader flag. """
        return toBool(self.get('bootLoader'))

    def setDiskSize(self, diskSize):
        """ Set disk size."""
        self['diskSize'] = diskSize

    def getDiskSize(self):
        """ Return disk size."""
        return self.get('diskSize')

    def setDirectAttachment(self, directAttachment):
        """ Set direct attachment method. """
        self['directAttachment'] = directAttachment

    def getDirectAttachment(self):
        """ Return direct attachment method. """
        return self.get('directAttachment')

    def setIndirectAttachment(self, indirectAttachment):
        """ Set indirect attachment method. """
        self['indirectAttachment'] = indirectAttachment

    def getIndirectAttachment(self):
        """ Return indirect attachment method. """
        return self.get('indirectAttachment')

    def setSanVolume(self, sanVolume):
        """ Set SAN volume method. """
        self['sanVolume'] = sanVolume

    def getSanVolume(self):
        """ Return SAN volume method. """
        return self.get('sanVolume')

    def setGrow(self, value=True):
        self['grow'] = toBool(value)

    def getGrow(self):
        return toBool(self.get('grow'))

    def setMaxSize(self, value):
        self['maxSize'] = value

    def getMaxSize(self):
        return self.get('maxSize')

    @staticmethod
    def getKeys():
        return [
            'id', 'name', 'softwareProfileId', 'device', 'mountPoint',
            'fsType', 'size', 'options', 'preserve', 'bootLoader',
            'diskSize', 'directAttachment', 'indirectAttachment',
            'sanVolume', 'maxSize', 'grow'
        ]
