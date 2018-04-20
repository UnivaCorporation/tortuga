#!/usr/bin/env python

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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest

from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi
from tortuga.objects.softwareProfile import SoftwareProfile


class UpdateSoftwareProfileCli(TortugaCli):
    """
    Update software profile command line interface.
    """

    # Software Profile Fetch Options
    # Skip nodes, components, and admins for update operations
    optionDict = {
        'partitions': True,
    }

    def parseArgs(self, usage=None):
        # Simple Options
        self.addOption('--name', dest='name',
                       help=_('Name of software profile'))
        self.addOption('--new-name', dest='newName',
                       help=_('New name for software profile'))
        self.addOption('--description', dest='description',
                       help=_('User description of this software profile'))
        self.addOption('--kernel', dest='kernel',
                       help=_('Kernel for software profile'))
        self.addOption('--kernel-parameters', dest='kernelParameters',
                       help=_('Kernel parameters for software profile'))
        self.addOption('--initrd', dest='initrd',
                       help=_('Initrd for software profile'))
        self.addOption('--min-nodes', dest='minNodes',
                       help=_('Minimum number of nodes required to remain in'
                              ' this profile.'))

        # Complex Options
        self.addOption('--add-partition', dest='addPartition',
                       help=_('A new partition to add to software profile'))

        self.addOption('--delete-partition', dest='deletePartition',
                       action='append',
                       help=_('A partition to delete from software profile'))

        self.addOption('--update-partition', dest='updatePartition',
                       help=_('Update existing partition in'
                              ' software profile'))

        # Partition Options
        self.addOption('--device', dest='device',
                       help=_('Hard disk and partition to use (ie 1.1)'))

        self.addOption('--mount-point', dest='mountPoint',
                       help=_('Mount point of partition'))

        self.addOption('--file-system', dest='fileSystem',
                       help=_('Filesystem type for partition'))

        self.addOption('--size', dest='size',
                       help=_('Size of partition.  Use \'MB\' suffix for'
                              ' megabytes.  Use \'GB\' suffix for gigabytes.'
                              ' Default without suffix is megabytes.'))

        self.addOption('--options', dest='options',
                       help=_('Options to pass to mount command'))

        self.addOption('--preserve', dest='preserve', action='store_true',
                       help=_('Format partition in image-based installation'))

        self.addOption('--no-preserve', dest='preserve',
                       action='store_false',
                       help=_('Do not format partition in image-based'
                              ' installation'))

        self.addOption('--boot-loader', dest='bootLoader',
                       action='store_true',
                       help=_('Install the bootloader on this partition for'
                              ' image-based installation'))

        self.addOption('--no-boot-loader', dest='bootLoader',
                       action='store_false',
                       help=_('Do not install bootloader on this partition'
                              ' for image-based installation'))

        self.addOption('--direct-attachment', dest='directAttachment',
                       help=_('Storage adapter which connects drive to node'))

        self.addOption('--indirect-attachment', dest='indirectAttachment',
                       help=_('Storage adapter which indirectly connects'
                              ' drive to a node. eg. how drive is connected to'
                              ' hypervisor for a VM'))

        self.addOption('--disk-size', dest='diskSize',
                       help=_('Size of disk that this partition will reside'
                              ' on.  Use \'MB\' suffix for megabytes.'
                              '  Use \'GB\' suffix for gigabytes. Default'
                              ' without suffix is megabytes. '))

        self.addOption('--san-volume', dest='sanVolume',
                       help=_('(optional) SAN volume to back device.'))

        self.addOption(
            '--grow', dest='grow', action='store_true',
            help=_('Tells the partition to grow to fill available space,'
                   ' or up to the maximum size setting.'))

        self.addOption(
            '--no-grow', dest='grow', action='store_false',
            help=_('Do not allow partition to grow'))

        self.addOption(
            '--max-size', dest='maxsize', type=int,
            help=_('The maximum size in megabytes when the partition'
                   ' is set to grow.'))

        # Or an xml file can be passed in
        self.addOption('--xml-file', dest='xmlFile',
                       help=_('A file pointing to an XML representation of'
                              ' hardware profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Updates software profile in the Tortuga system.
"""))

        software_profile_name = self.getArgs().name

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        if self.getArgs().xmlFile:
            # An XML file was provided as input...start with that...
            f = open(self.getArgs().xmlFile, 'r')
            try:
                xmlString = f.read()
            finally:
                f.close()
            try:
                sp = SoftwareProfile.getFromXml(xmlString)
            except Exception as ex:
                sp = None
                self.getLogger().debug('Error parsing xml %s' % ex)

            if sp is None:
                raise InvalidCliRequest(
                    _('The file "%s" does not contain a valid software'
                      ' profile') % (self.getArgs().xmlFile))
        else:
            if software_profile_name is None:
                raise InvalidCliRequest(_('Missing software profile name'))

            sp = api.getSoftwareProfile(software_profile_name,
                                        UpdateSoftwareProfileCli.optionDict)

        if self.getArgs().newName is not None:
            sp.setName(self.getArgs().newName)
        if self.getArgs().description is not None:
            sp.setDescription(self.getArgs().description)
        if self.getArgs().kernel is not None:
            sp.setKernel(self.getArgs().kernel)
        if self.getArgs().kernelParameters is not None:
            sp.setKernelParams(self.getArgs().kernelParameters)
        if self.getArgs().initrd is not None:
            sp.setInitrd(self.getArgs().initrd)
        if self.getArgs().minNodes is not None:
            sp.setMinNodes(self.getArgs().minNodes)
        if self.getArgs().deletePartition is not None:
            from tortuga.objects.tortugaObject import TortugaObjectList
            out = TortugaObjectList()
            for p in sp.getPartitions():
                for dp in self.getArgs().deletePartition:
                    if dp == p.getName():
                        # Skip over this item..its getting deleted
                        break
                else:
                    # Not a partition we are deleting
                    out.append(p)
            sp.setPartitions(out)

        partitionObject = None
        if self.getArgs().updatePartition:
            if self.getArgs().addPartition:
                raise InvalidCliRequest(
                    _('Must provide only one of --update-partition and'
                      ' --add-partition'))

            for p in sp.getPartitions():
                if p.getName() == self.getArgs().updatePartition:
                    partitionObject = p
                    break
            else:
                raise InvalidCliRequest(
                    _('Cannot update non-existent partition "%s"') % (
                        self.getArgs().updatePartition))

        if self.getArgs().addPartition:
            from tortuga.objects.partition import Partition
            partitionObject = Partition()
            partitionObject.setName(self.getArgs().addPartition)
            sp.getPartitions().append(partitionObject)
            if self.getArgs().device is None or \
                    self.getArgs().fileSystem is None or \
                    self.getArgs().size is None:
                raise InvalidCliRequest(
                    _('--device, --file-system, and --size options required'
                      ' with --add-partition'))

        if self.getArgs().grow:
            if not partitionObject:
                raise InvalidCliRequest(
                    _('The --grow/--no-grow options is only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setGrow(self.getArgs().grow)

        if self.getArgs().maxsize:
            if not partitionObject:
                raise InvalidCliRequest(
                    _('The --max-size option is only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setMaxSize(self.getArgs().maxsize)

        if self.getArgs().device is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('The --device option is only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setDevice(self.getArgs().device)

        if self.getArgs().mountPoint is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--mount-point option only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setMountPoint(self.getArgs().mountPoint)

        if self.getArgs().fileSystem is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('The --file-system option only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setFsType(self.getArgs().fileSystem)

        if self.getArgs().size is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--size option only allowed with --update-partition or'
                      ' --add-partition'))

            partitionObject.setSize(self._parseDiskSize(self.getArgs().size))

        if self.getArgs().options is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--options option only allowed with --update-partition'
                      ' or --add-partition'))

            partitionObject.setOptions(self.getArgs().options)

        if self.getArgs().directAttachment is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--direct-attachment option only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setDirectAttachment(self.getArgs().directAttachment)

        if self.getArgs().indirectAttachment is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--indirect-attachment option only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setIndirectAttachment(
                self.getArgs().indirectAttachment)

        if self.getArgs().diskSize is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--disk-size option only allowed with'
                      ' --update-partition or --add-partition'))

            try:
                partitionObject.setDiskSize(
                    self._parseDiskSize(self.getArgs().diskSize))
            except ValueError:
                raise InvalidCliRequest(_('Invalid --disk-size argument'))

        if self.getArgs().sanVolume is not None:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--san-volume option only allowed with'
                      ' --update-partition or --add-partition'))

            partitionObject.setSanVolume(self.getArgs().sanVolume)

        if self.getArgs().preserve is None:
            if self.getArgs().addPartition is not None:
                raise InvalidCliRequest(
                    _('--preserve or --no-preserve must be specified when'
                      ' adding a new partition.'))
        else:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--preserve and --no-preserve options are only allowed'
                      ' with --update-partition or --add-partition'))

            partitionObject.setPreserve(self.getArgs().preserve)

        if self.getArgs().bootLoader is None:
            if self.getArgs().addPartition is not None:
                raise InvalidCliRequest(
                    _('--boot-loader or --no-boot-loader must be specified'
                      ' when adding a new partition.'))
        else:
            if partitionObject is None:
                raise InvalidCliRequest(
                    _('--boot-loader and --no-boot-loader options only'
                      ' allowed with --update-partition or --add-partition'))

            partitionObject.setBootLoader(self.getArgs().bootLoader)

        api.updateSoftwareProfile(sp)


def main():
    UpdateSoftwareProfileCli().run()
