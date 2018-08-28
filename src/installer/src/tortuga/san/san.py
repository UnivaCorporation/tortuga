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

# pylint: disable=logging-not-lazy,no-name-in-module,no-self-use

import os.path
import uuid
import configparser
import logging
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.volumeAlreadyMapped import VolumeAlreadyMapped
from tortuga.exceptions.volumeDoesNotExist import VolumeDoesNotExist
from tortuga.exceptions.volumeNotMapped import VolumeNotMapped
from tortuga.exceptions.volumeStillAttached import VolumeStillAttached
from tortuga.exceptions.deletePersistentVolumeFailed \
    import DeletePersistentVolumeFailed
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.objects.volume import Volume
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.config.configManager import ConfigManager


class DriveInfo(object):
    def __init__(self, device=None, targetHost=None, volume=None):
        self._device = device
        self._targetHost = targetHost
        self._volume = volume

    @property
    def volume(self):
        return self._volume

    @property
    def device(self):
        return self._device

    @property
    def targetHost(self):
        return self._targetHost


class DiskChangeOperations(object):
    def __init__(self):
        self.__removed = {}
        self.__added = {}
        self.__unchanged = {}

    @property
    def removed(self):
        return self.__removed

    @property
    def added(self):
        return self.__added

    @property
    def unchanged(self):
        return self.__unchanged


class San(object): \
        # pylint: disable=too-many-public-methods
    '''
    This class creates and tears down SAN connections
    '''

    DEFAULT_CACHE_FILE = os.path.join(
        ConfigManager().getKitConfigBase(), 'san-data.conf')

    VOLUME_SECTION_NAME = 'volumes'

    def __init__(self):
        self._logger = logging.getLogger(
            'tortuga.san.%s' % self.__class__.__name__)

    def __read_cache_file(self, filename=None):
        if filename is None:
            filename = self.DEFAULT_CACHE_FILE

        self.getLogger().debug(
            '[%s] Reading cache file [%s]' % (
                self.__class__.__name__, filename))

        cfg = configparser.ConfigParser()

        cfg.read(filename)

        return cfg

    def __write_cache_file(self, config, filename=None):
        if filename is None:
            filename = self.DEFAULT_CACHE_FILE

        self.getLogger().debug(
            '[%s] Writing cache file [%s]' % (
                self.__class__.__name__, filename))

        with open(filename, 'w') as fp:
            config.write(fp)

    def __getStorageAdapter(self, adapter):
        from tortuga.resourceAdapter.san import storageAdapterFactory
        return storageAdapterFactory.get_api(adapter)

    def __getDriveInfo(self, nodeName, driveNumber, config=None):
        """

        Returns:
            DriveInfo
        """
        if config is None:
            config = self.__read_cache_file()

        volume_id, device, targetHost = config.get(
            nodeName, str(driveNumber)).split()

        return DriveInfo(
            device=device, targetHost=targetHost,
            volume=self.__get_volume(volume_id, config))

    def __get_volume(self, volume_id, config=None):
        """
        Returns:
            Volume object

        Raises:
            VolumeDoesNotExist
        """

        if config is None:
            config = self.__read_cache_file()

        try:
            size, storageAdapter, adapterVolume, persistent, shared = \
                config.get(self.VOLUME_SECTION_NAME, volume_id).split()

            return Volume(
                volume_id=volume_id.lower(),
                size=int(size),
                storageAdapter=storageAdapter,
                adapterVolume=adapterVolume,
                persistent=persistent.lower() == 'true',
                shared=shared.lower() == 'true'
            )
        except (configparser.NoOptionError, configparser.NoSectionError):
            raise VolumeDoesNotExist(
                'Volume [%s] does not exist' % (volume_id))
        except ValueError:
            raise VolumeDoesNotExist(
                'Volume [%s] entry malformed' % (volume_id))

    def __getAllNodeDrives(self, nodeName):
        config = self.__read_cache_file()

        if not config.has_section(nodeName):
            return []

        return config.options(nodeName)

    def __checkVolumeTargetHost(self, volume, targetHost, config=None):
        if config is None:
            config = self.__read_cache_file()

        if config.has_section(volume):
            # So the volume section exists...
            if config.has_option(volume, targetHost):
                # We this volume is already mapped to this drive
                # lets see what nodes we have there.
                parts = config.get(volume, targetHost).split(' ')

                curDevice = parts[0]

                nodes = []

                if len(parts) > 1:
                    nodes = parts[1].split(',')

                return nodes, curDevice

        return [], None

    def __getVolumeTargetHosts(self, volume, config=None):
        if config is None:
            config = self.__read_cache_file()

        hosts = []
        nodes = []

        if not config.has_section(volume):
            return hosts, nodes

        for item in config.items(volume):
            indirectNodes, _ = self.__checkVolumeTargetHost(
                volume, item[0], config)

            nodes.extend(indirectNodes)

            hosts.append(item[0])

        return hosts, nodes

    def __addTargetHostMapping(self, volume, targetHost, device, nodeName,
                               config=None):
        if config is None:
            config = self.__read_cache_file()

        # Check if the volume is currently connected
        currentNodes, curDevice = self.__checkVolumeTargetHost(
            volume, targetHost, config)

        if curDevice is None:
            curDevice = device

        if nodeName not in currentNodes:
            currentNodes.append(nodeName)

        if not config.has_section(volume):
            config.add_section(volume)

        config.set(
            volume, targetHost, '%s %s' % (curDevice, ','.join(currentNodes)))

        self.__write_cache_file(config)

    def __removeTargetHostMapping(self, volume, targetHost, nodeName,
                                  config=None):
        if config is None:
            config = self.__read_cache_file()

        # Check if the volume is currently connected
        currentNodes, device = self.__checkVolumeTargetHost(
            volume, targetHost, config)

        if nodeName in currentNodes:
            currentNodes.remove(nodeName)

        if not config.has_section(volume):
            config.add_section(volume)

        if not currentNodes:
            # Remove this target host
            config.remove_option(volume, targetHost)

            if not config.items(volume):
                # Also remove the section
                config.remove_section(volume)
        else:
            config.set(
                volume, targetHost, '%s %s' % (device, ','.join(currentNodes)))

        self.__write_cache_file(config)

    def __updateNodeVolume(self, nodeName, driveNumber, volume, device,
                           targetHost):
        config = self.__read_cache_file()

        if not config.has_section(nodeName):
            config.add_section(nodeName)

        config.set(
            nodeName, str(driveNumber),
            '%s %s %s' % (volume, device, targetHost))

        # Also add the volume section for tracking all of the hosts that
        # have this drive mounted
        self.__write_cache_file(config)

    def __removeVolumeMapping(self, volume, nodeName, driveNumber): \
            # pylint: disable=unused-argument
        config = self.__read_cache_file()

        config.remove_option(nodeName, str(driveNumber))

        if not config.items(nodeName):
            config.remove_section(nodeName)

        self.__write_cache_file(config)

    def __removeVolume(self, volume):
        config = self.__read_cache_file()

        config.remove_option(self.VOLUME_SECTION_NAME, volume)

        self.__write_cache_file(config)

    def __addStorageVolume(self, volume, size, storageAdapter,
                           adapterVolume, persistent, shared):
        # Grab config file
        config = self.__read_cache_file()

        if not config.has_section(self.VOLUME_SECTION_NAME):
            config.add_section(self.VOLUME_SECTION_NAME)

        config.set(
            self.VOLUME_SECTION_NAME, volume, '%s %s %s %s %s' % (
                size, storageAdapter, adapterVolume, persistent, shared))

        self.__write_cache_file(config)

    def __updateStorageVolume(self, volume, size, storageAdapter,
                              adapterVolume, persistent, shared):
        # Add can do updates too
        self.__addStorageVolume(
            volume, size, storageAdapter, adapterVolume, persistent, shared)

    def __getNodeDriveInfo(self, nodeName):
        # Grab config file
        config = self.__read_cache_file()

        # Lookup existing drives
        if not config.has_section(nodeName):
            return {}

        if not config.has_section(nodeName):
            config.add_section(nodeName)

        previousHardDrives = {}

        previousHardDrivesConfig = config.items(nodeName)

        self.getLogger().debug(
            '[%s] Previous drives for node [%s]: [%s]' % (
                self.__class__.__name__, nodeName, previousHardDrivesConfig))

        for drive_number, _ in previousHardDrivesConfig:
            driveinfo = self.__getDriveInfo(nodeName, drive_number, config)

            previousHardDrives[drive_number] = {
                'device': driveinfo.device,
                'volume': driveinfo.volume,
                'targetHost': driveinfo.targetHost,
            }

        return previousHardDrives

    def __process_persistent_drives(self, previousHardDrives,
                                    swpPersistentDrives, diskChanges,
                                    deleteNode, driveNumbers):
        # Find an open slot for persistent drives
        nextDrive = 1 if not driveNumbers else int(driveNumbers[-1]) + 1

        for driveNumber in previousHardDrives:
            if previousHardDrives[driveNumber]['volume'].getPersistent():
                self.getLogger().debug(
                    '[%s] Looking for [%s] in [%s]' % (
                        self.__class__.__name__,
                        previousHardDrives[driveNumber]['volume'],
                        swpPersistentDrives))

                if previousHardDrives[driveNumber]['volume'] in \
                        swpPersistentDrives:
                    # Swp drives are already addressed
                    continue

                # Put all other persistent drives at the end...
                if deleteNode:
                    diskChanges.removed[str(driveNumber)] = \
                        previousHardDrives[driveNumber]

                    continue

                nextDrive += 1

                diskChanges.unchanged[str(nextDrive)] = \
                    previousHardDrives[driveNumber]

                continue

            if driveNumber not in driveNumbers:
                # If we aren't persistent and aren't in the list,
                # remove the drive

                volume = previousHardDrives[driveNumber]['volume']

                # Delete drive
                diskChanges.removed[driveNumber] = {
                    'size': volume.getSize(),
                    'adapter': volume.getStorageAdapter(),
                    'device': previousHardDrives[driveNumber]['device']
                }

    def discoverStorageChanges(self, dbNode, deleteNode=False,
                               hardwareprofile=None, softwareprofile=None): \
            # pylint: disable=unused-argument
        """
        Raises:
            VolumeDoesNotExist
        """

        softwareprofile = softwareprofile if softwareprofile else \
            dbNode.softwareprofile

        driveNumbers = []
        swpPersistentDrives = []

        previousHardDrives = self.__getNodeDriveInfo(dbNode.name)

        diskChanges = DiskChangeOperations()

        # Iterate over partitions defined in software profile, unless node is
        # marked for deletion. Extract 'driveNumber' from partition
        # device name.
        for driveNumber, partition in [] if deleteNode else [
                (partition.device.split('.')[0], partition)
                for partition in softwareprofile.partitions]:
            # Look for drives
            if driveNumber in driveNumbers:
                continue

            # We haven't looked at this drive number yet
            driveNumbers.append(driveNumber)

            # Override the storage adapter with the volumes adapter
            storageAdapter = self.getVolume(partition.sanVolume).\
                getStorageAdapter() if partition.sanVolume else \
                partition.indirectAttachment

            # If this drive already existed for this node, check to see
            # if it changed
            if driveNumber not in previousHardDrives:
                # Add new drive
                diskChanges.added[driveNumber] = {
                    'size': partition.diskSize,
                    'adapter': storageAdapter,
                    'sanVolume': partition.sanVolume,
                }

                continue

            volume = previousHardDrives[driveNumber]['volume']

            # If we run into a persistent volume in here we need to
            # move it to the end...
            if volume.getPersistent():
                if partition.sanVolume == volume:
                    # Unchanged....
                    diskChanges.unchanged[driveNumber] = {
                        'size': partition.diskSize,
                        'adapter': storageAdapter,
                        'device': previousHardDrives[driveNumber]['device']
                    }
                else:

                    # Replacing switching things arround
                    diskChanges.removed[driveNumber] = {
                        'size': volume.getSize(),
                        'adapter': volume.getStorageAdapter(),
                        'device': previousHardDrives[driveNumber]['device']
                    }

                    # Add new drive
                    diskChanges.added[driveNumber] = {
                        'size': partition.diskSize,
                        'adapter': storageAdapter,
                        'sanVolume': partition.sanVolume,
                    }

                # This drive we need to skip over when we look for
                # node base persisted volumes
                swpPersistentDrives.append(volume)

                continue

            # Drive existed, let's check its parameters
            if storageAdapter == volume.getStorageAdapter() and \
                    partition.diskSize == volume.getSize():
                # Drives are the same, don't need to change it
                diskChanges.unchanged[driveNumber] = {
                    'size': partition.diskSize,
                    'adapter': storageAdapter,
                    'device': previousHardDrives[driveNumber]['device']
                }

                continue

            # Drives are different, need to remove the old
            # one and create the new one
            diskChanges.removed[driveNumber] = {
                'size': volume.getSize(),
                'adapter': volume.getStorageAdapter(),
                'device': previousHardDrives[driveNumber]['device']
            }

            # Add new drive
            diskChanges.added[driveNumber] = {
                'size': partition.diskSize,
                'adapter': storageAdapter,
                'sanVolume': partition.sanVolume,
            }

        # Sort all of our drive numbers
        list.sort(driveNumbers)

        # Take care of any other pre-existing drives
        self.__process_persistent_drives(
            previousHardDrives, swpPersistentDrives, diskChanges, deleteNode,
            driveNumbers)

        self.getLogger().debug(
            '[%s] Returning diskChanges %s' % (
                self.__class__.__name__, diskChanges))

        return {
            'added': diskChanges.added,
            'unchanged': diskChanges.unchanged,
            'removed': diskChanges.removed,
        }

    def addDrive(self, dbNode, storageAdapter, driveNumber, size,
                 sanVolume):
        """
        Raises:
            VolumeDoesNotExist
        """

        # If a san volume is being passed just make sure it exists
        volume = self.getVolume(sanVolume) if sanVolume else \
            self.addVolume(
                storageAdapter,
                size,
                "%s-%s" % (dbNode.name, driveNumber),
                False)

        self.getLogger().debug(
            '[%s] SAN DB add drive: node [%s], driveNumber [%s],'
            ' volume [%s]' % (
                self.__class__.__name__, dbNode.name, driveNumber,
                volume.getId()))

        # Create the association
        self.__updateNodeVolume(
            dbNode.name, driveNumber, volume.getId(), 'device_placeholder',
            'node_placeholder')

        return volume.getId()

    def addVolume(self, storageAdapter, size, nameFormat='*',
                  persistent=False, shared=False):
        adapterVolume = 'volume_placeholder'

        # IF there is a custom storage adapter, use it to create the storage
        if storageAdapter != 'default':
            # Lookup storage adapter
            adapter = self.__getStorageAdapter(storageAdapter)

            # Have the adapter allocate the space
            adapterVolume = adapter.allocateVolume(size, nameFormat)

        # Create a volume ID
        volume = str(uuid.uuid1())

        self.getLogger().debug(
            '[%s] SAN DB add vol: adapter [%s], volume [%s] size [%s]'
            ' persistent [%s]' % (
                self.__class__.__name__, storageAdapter, volume, size,
                persistent))

        # Save the new volume
        self.__addStorageVolume(
            volume, size, storageAdapter, adapterVolume, persistent, shared)

        return Volume(size=size,
                      volume_id=volume,
                      storageAdapter=storageAdapter,
                      adapterVolume=adapterVolume,
                      persistent=persistent,
                      shared=shared)

    def deleteDrive(self, dbNode, driveNumber):
        driveinfo = self.__getDriveInfo(dbNode.name, driveNumber)

        # unmap the volume first
        self.unmapDrive(dbNode, driveNumber=driveNumber)

        # Delete the volume if we should...
        try:
            self.deleteVolume(driveinfo.volume.getId())
        except DeletePersistentVolumeFailed:
            # This is ok...we don't want to delete persistent volumes here
            pass

        config = self.__read_cache_file()

        if config.has_section(dbNode.name) and \
                not config.options(dbNode.name):
            # Remove the section after removing the last option
            config.remove_section(dbNode.name)

            self.__write_cache_file(config)

        self.getLogger().debug(
            '[%s] SAN DB remove mapping: node [%s], driveNumber [%s],'
            ' adapter [%s]' % (
                self.__class__.__name__, dbNode.name, driveNumber,
                driveinfo.volume.getStorageAdapter()))

    def updateVolume(self, volume, newPersistent, newShared):
        """
        Raises:
            VolumeStillAttached
        """

        volinfo = self.__get_volume(volume)

        # Now make sure that this volume isn't currently attached
        hosts, _ = self.__getVolumeTargetHosts(volume)

        if hosts:
            raise VolumeStillAttached(
                'Unable to update volume: Volume [%s] is still attached'
                ' to %d host(s)' % (volume, len(hosts)))

        self.__updateStorageVolume(
            volume, volinfo.getSize(), volinfo.getStorageAdapter(),
            volinfo.getAdapterVolume(), newPersistent, newShared)

    def deleteVolume(self, volume, force=False):
        """
        Raises:
            VolumeStillAttached
            DeletePersistentVolumeFailed
        """

        volinfo = self.__get_volume(volume)

        if volinfo.getPersistent() and not force:
            raise DeletePersistentVolumeFailed(
                'Error deleting volume: Force option is required to delete'
                ' a persistent volume')

        # Now make sure that this volume isn't currently attached
        hosts, _ = self.__getVolumeTargetHosts(volume)

        if hosts:
            raise VolumeStillAttached(
                'Volume [%s] is still attached to %d host(s)' % (
                    volume, len(hosts)))

        # IF there is a custom storage adapter, use it to remove the
        # storage
        if volinfo.getStorageAdapter() != 'default':
            # Delete the volume
            self.__getStorageAdapter(volinfo.getStorageAdapter()).\
                deleteVolume(volinfo.getAdapterVolume())

        # Now remove the volume
        self.__removeVolume(volume)

    def connectStorageVolume(self, dbNode, volume, targetHost):
        """
        Raises:
            UnsupportedOperation
            VolumeNotMapped
            VolumeDoesNotExist
        """

        for drive, _, _ in self.getNodeVolumeInfo(dbNode, volume):
            try:
                return self.connectStorage(dbNode, drive, targetHost)
            except UnsupportedOperation:
                raise
            except Exception:
                self.getLogger().debug(
                    '[%s] Error getting info for node [%s] drive [%s]' % (
                        self.__class__.__name__, dbNode.name, drive))

                self.getLogger().exception(
                    'Exception raised attempting to connect storage volume')

                raise

        # Make sure the volume exists
        self.getVolume(volume)

        raise VolumeNotMapped(
            'Volume [%s] not mapped to %s' % (volume, dbNode.name))

    def getNodeVolumeInfo(self, dbNode, volume):
        driveNumbers = []

        for drive in self.__getAllNodeDrives(dbNode.name):
            try:
                driveinfo = self.__getDriveInfo(dbNode.name, drive)

                self.getLogger().debug(
                    '[%s] Comparing drive [%s] volume [%s] to [%s]' % (
                        self.__class__.__name__, drive, driveinfo.volume,
                        volume))

                if driveinfo.volume.getId() == volume:
                    vol = Volume(
                        size=driveinfo.volume.getSize(),
                        volume_id=volume,
                        storageAdapter=driveinfo.volume.getStorageAdapter(),
                        adapterVolume=driveinfo.volume.getAdapterVolume(),
                        persistent=driveinfo.volume.getPersistent())

                    driveNumbers.append((drive, driveinfo.device, vol))
            except Exception:
                self.getLogger().debug(
                    '[%s] Error getting info for node [%s] drive [%s]' % (
                        self.__class__.__name__, dbNode.name, drive))

        return driveNumbers

    def connectStorage(self, dbNode, driveNumber, targetHost):
        """
        Raise:
            UnsupportedOperation
        """

        driveinfo = self.__getDriveInfo(dbNode.name, driveNumber)

        # Lookup storage adapter
        adapter = self.__getStorageAdapter(
            driveinfo.volume.getStorageAdapter())

        # Get the list of all mounts for this volume
        _, mappedNodes = self.__getVolumeTargetHosts(driveinfo.volume)

        self.getLogger().debug(
            '[%s] Volume [%s] is mapped to nodes [%s]' % (
                self.__class__.__name__, driveinfo.volume, mappedNodes))

        # Check if the device is already connected on the new hypervisor
        nodes, device = self.__checkVolumeTargetHost(
            driveinfo.volume, targetHost)

        self.getLogger().debug(
            '[%s] Volume [%s] is connected on target host [%s] at [%s]'
            ' for nodes [%s]' % (
                self.__class__.__name__, driveinfo.volume, targetHost,
                driveinfo.device, nodes))

        # If this is a multi mount request and not shared we need to bail
        if mappedNodes:
            # This volume is attached somewhere
            if not driveinfo.volume.getShared():
                # Check if this is a double connect
                if nodes and dbNode.name in nodes:
                    # OK...this is is a non-shared device but this node was
                    # already connected so we are ok
                    newDevice = adapter.connectVolume(
                        driveinfo.volume.getAdapterVolume(), targetHost, False)

                    if newDevice != device:
                        raise UnsupportedOperation(
                            'Inconsistent state for volume [%s] on node'
                            ' [%s].  The node must be shutdown.' % (
                                driveinfo.volume, dbNode.name))

                    self.__addTargetHostMapping(
                        driveinfo.volume, targetHost, device, dbNode.name)

                    self.__updateNodeVolume(
                        dbNode.name, driveNumber, driveinfo.volume, device,
                        targetHost)

                    return device

                if dbNode.name in mappedNodes:
                    # So the node is most likely being migrated as it is
                    # mapped but not connected on the targetHost.  We can
                    # just continue
                    pass
                else:
                    raise UnsupportedOperation(
                        'Unable to multi-mount non-shared volume')

        if driveinfo.volume.getShared() or nodes:
            # Have the adapter connect the device to the node
            multiMount = False
            if targetHost != dbNode.name:
                if driveinfo.volume.getShared():
                    multiMount = dbNode.name

            device = adapter.connectVolume(
                driveinfo.volume.getAdapterVolume(), targetHost, multiMount)

        self.__addTargetHostMapping(
            driveinfo.volume, targetHost, device, dbNode.name)

        self.__updateNodeVolume(
            dbNode.name, driveNumber, driveinfo.volume, device, targetHost)

        return device

    def disconnectStorageVolume(self, dbNode, volume, connectedNodeName=None):
        """
        Raises:
            VolumeDoesNotExist
            VolumeNotMapped
        """

        drives = self.getNodeVolumeInfo(dbNode, volume)

        if not drives:
            # Make sure the volume exists
            self.getVolume(volume)

            raise VolumeNotMapped(
                'Volume [%s] is not mapped to %s' % (volume, dbNode.name))

        for drive, _, _ in drives:
            try:
                # Disconnect this drive
                self.disconnectStorage(dbNode, drive, connectedNodeName)
            except Exception as ex:
                self.getLogger().debug(
                    '[%s] Error getting info for node [%s] drive [%s]' % (
                        self.__class__.__name__, dbNode.name, drive))

                self.getLogger().exception(ex)

                raise

    def disconnectStorage(self, dbNode, driveNumber,
                          connectedNodeName=None):
        driveinfo = self.__getDriveInfo(dbNode.name, driveNumber)

        # IF the disconnect is for a specific node
        if connectedNodeName:
            attachedNodeName = connectedNodeName

        # Lookup storage adapter
        adapter = self.__getStorageAdapter(
            driveinfo.volume.getStorageAdapter())

        # Check if the device is connected by multiple nodes on the current
        # hypervisor
        nodes, _ = self.__checkVolumeTargetHost(
            driveinfo.volume, attachedNodeName)

        self.getLogger().debug(
            '[%s] Volume [%s] is connected on target host [%s] at [%s]'
            ' for nodes [%s]' % (
                self.__class__.__name__, driveinfo.volume, attachedNodeName,
                driveinfo.device, [tmpNode.name for tmpNode in nodes]))

        if driveinfo.volume.getShared() or \
                (len(nodes) == 1 and dbNode.name in nodes):
            # Have the adapter disconnect the device from the node
            multiMount = False

            if attachedNodeName != dbNode.name:
                if driveinfo.volume.getShared():
                    multiMount = dbNode.name

            adapter.disconnectVolume(
                driveinfo.volume.getAdapterVolume(), attachedNodeName,
                driveinfo.device, multiMount)

        # Remove the mapping for this device
        self.__removeTargetHostMapping(
            driveinfo.volume, attachedNodeName, dbNode.name)

        # Only update the config file if this wasn't a overriding disconnect
        if not connectedNodeName:
            self.__updateNodeVolume(
                dbNode.name, driveNumber, driveinfo.volume,
                'device_placeholder', 'node_placeholder')

    def getNodeVolumes(self, nodeName):
        vols = TortugaObjectList()

        for drive in self.__getAllNodeDrives(nodeName):
            try:
                driveinfo = self.__getDriveInfo(nodeName, drive)

                vols.append(driveinfo.volume)
            except Exception as ex:
                self.getLogger().debug(
                    '[%s] Error getting info for node [%s] drive [%s]:'
                    ' %s' % (self.__class__.__name__, nodeName, drive, ex))

        return vols

    def supportsCheckpoint(self, dbNode, isDefaultCheckpointable):
        # Find out what kind of disks we need for this node

        nodePartitions = dbNode.softwareprofile.partitions

        driveNumbers = []
        drives = {}

        for partition in nodePartitions:
            # We skip all drives associated with persistent volumes
            if not partition.sanVolume:
                # Look for drives
                driveNumber = partition.device.split('.')[0]

                if driveNumber not in driveNumbers:
                    # We haven't looked at this drive number yet
                    driveNumbers.append(driveNumber)

                    # Get the storage adapter for this drive
                    storageAdapter = partition.getIndirectAttachment()
                    drives[driveNumber] = storageAdapter

        for drive in drives:
            supportsCheckpoint = True

            # Lookup storage adapter
            if drives[drive] != 'default':
                adapter = self.__getStorageAdapter(drives[drive])

                # See if this adapter supports checkpointing
                if not adapter.supportsCheckpoint():
                    supportsCheckpoint = False
                    break
            else:
                if not isDefaultCheckpointable:
                    supportsCheckpoint = False
                    break

        return supportsCheckpoint

    def snapshotVolume(self, volume):
        # Method for snapshotting storage volume
        pass

    def revertVolume(self, volume):
        # Method for reverting a storage volume
        pass

    def checkpointNode(self, dbNode, isDefaultCheckpointable):
        """
        Raises:
            UnsupportedOperation
        """

        if not self.supportsCheckpoint(dbNode, isDefaultCheckpointable):
            raise UnsupportedOperation(
                'Node [%s] does not support checkpointing' % (dbNode.name))

        self.getLogger().debug('[%s] Checkpointing node [%s]' % (
            self.__class__.__name__, dbNode.name))

        # Find out what kind of disks we need for this node
        driveNumbers = []
        drives = {}

        for driveNumber, partition in \
                [(partition.device.split('.')[0], partition)
                 for partition in dbNode.softwareprofile.partitions]:
            # Look for drives
            # driveNumber = partition.device.split('.')[0]

            if driveNumber in driveNumbers:
                continue

            # We haven't looked at this drive number yet
            driveNumbers.append(driveNumber)

            # Get the storage adapter for this drive
            driveinfo = self.__getDriveInfo(dbNode.name, driveNumber)

            # Only include non-persistent drives in checkpoint
            if not driveinfo.volume.getPersistent():
                drives[driveNumber] = (driveinfo.volume.getStorageAdapter(),
                                       driveinfo.volume.getAdapterVolume())

        for drive in drives:
            storageAdapter, adapterVolume = drives[drive]

            # Lookup storage adapter
            if storageAdapter != 'default':
                adapter = self.__getStorageAdapter(storageAdapter)

                # Checkpoint drive
                adapter.checkpointDrive(adapterVolume)

            # We don't do anything here if storageAdapter == 'default'.  If
            # there are default drives the node adapter needs to take care
            # of checkpointing them.

    def revertDrivesToCheckpoint(self, dbNode, isDefaultCheckpointable):
        """
        Raises:
            UnsupportedOperation
        """

        if not self.supportsCheckpoint(dbNode, isDefaultCheckpointable):
            raise UnsupportedOperation(
                'Node [%s] does not support checkpointing' % (dbNode.name))

        self.getLogger().debug(
            '[%s] Reverting node [%s] to checkpoint' % (
                self.__class__.__name__, dbNode.name))

        # Find out what kind of disks we need for this node
        nodePartitions = dbNode.softwareprofile.partitions

        driveNumbers = []
        drives = {}

        for partition in nodePartitions:
            # Look for drives
            driveNumber = partition.device.split('.')[0]

            if driveNumber in driveNumbers:
                continue

            # We haven't looked at this drive number yet
            driveNumbers.append(driveNumber)

            # Get the storage adapter for this drive
            driveinfo = self.__getDriveInfo(dbNode.name, driveNumber)

            # Only include non-persistent drives in revert checkpoint
            if not driveinfo.volume.getPersistent():
                drives[driveNumber] = (driveinfo.volume.getStorageAdapter(),
                                       driveinfo.volume.getAdapterVolume())

        for drive in drives:
            storageAdapter, adapterVolume = drives[drive]

            # Lookup storage adapter
            if storageAdapter != 'default':
                adapter = self.__getStorageAdapter(storageAdapter)

                # Checkpoint drive
                adapter.revertDriveToCheckpoint(adapterVolume)

            # We don't do anything here for the default condition..  If
            # there are default drives the node adapter needs to take care
            # of reverting them.

    # Associate a volume with a node
    def mapDrive(self, dbNode, volume):
        '''
        Create a mapping between a node drive and a volume

        Raises:
            VolumeDoesNotExist
            VolumeAlreadyMapped
        '''

        # Make sure the volume exists
        self.getVolume(volume)

        # Make sure the volume isn't already mapped
        if self.getNodeVolumeInfo(dbNode, volume):
            raise VolumeAlreadyMapped(
                'Volume [%s] is already mapped to %s' % (volume, dbNode.name))

        # Find the next open drive number
        disks = self.__getAllNodeDrives(dbNode.name)

        openDriveNumber = 1

        for driveNumber in disks:
            if openDriveNumber <= int(driveNumber):
                openDriveNumber = int(driveNumber) + 1

        # Create the association
        self.__updateNodeVolume(
            dbNode.name, str(openDriveNumber), volume,
            'device_placeholder', 'node_placeholder')

        return openDriveNumber

    def unmapDrive(self, dbNode, volume=None, driveNumber=None):
        '''
        Remove a mapping between a node drive and a volume

        Raises:
            InvalidArgument
            VolumeDoesNotExist
            VolumeNotMapped
        '''

        if volume is None and driveNumber is None:
            raise InvalidArgument(
                'Either volume or driveNumber needs to be provided')

        driveNumbers = [
            drive for drive in self.__getAllNodeDrives(dbNode.name)
            if self.__getDriveInfo(
                dbNode.name, drive).volume.getId() == volume.lower()] \
            if volume else [driveNumber]

        if not driveNumbers:
            # Make sure the volume exists
            self.getVolume(volume)

            raise VolumeNotMapped(
                'Volume [%s] not mapped to %s' % (volume, dbNode.name))

        for drive in driveNumbers:
            # Remove the association
            self.__removeVolumeMapping(volume, dbNode.name, drive)

    def getVolumeList(self):
        return self.__getVolumeHelper()

    def getVolume(self, volume):
        '''
        Raises:
            VolumeDoesNotExist
        '''

        return self.__getVolumeHelper(volume)[0]

    def __getVolumeHelper(self, queryVolume=None):
        """
        Returns a list of 0 or more volumes if 'queryVolume' is None, otherwise
        returns a list containing the requested volume.  Raises exception if
        'queryVolume' is set and no volumes match.

        Raises:
            VolumeDoesNotExist
        """

        config = self.__read_cache_file()

        volumes = TortugaObjectList()

        if not config.has_section(self.VOLUME_SECTION_NAME):
            return volumes

        for item in config.items(self.VOLUME_SECTION_NAME):
            volume = item[0]

            volinfo = self.__get_volume(volume, config)

            if queryVolume:
                if volume == queryVolume.lower():
                    volumes.append(volinfo)
                    break
            else:
                volumes.append(volinfo)

        if not volumes and queryVolume is not None:
            raise VolumeDoesNotExist(
                'Volume [%s] does not exist' % (queryVolume.lower()))

        return volumes

    def getLogger(self):
        return self._logger
