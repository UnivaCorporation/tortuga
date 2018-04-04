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

# pylint: disable=no-member

import argparse
import json

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.softwareprofile.softwareProfileFactory \
    import getSoftwareProfileApi
from tortuga.hardwareprofile.hardwareProfileFactory \
    import getHardwareProfileApi


class GetSoftwareProfileCli(TortugaCli):
    """
    Get software profile command line interface.
    """

    def __init__(self):
        super(GetSoftwareProfileCli, self).__init__()

        self.swprofileapi = None
        self.hwprofileapi = None

    def parseArgs(self, usage=None):
        softwareProfileAttrGroup = _('Software Profile Attribute Options')

        self.addOptionGroup(softwareProfileAttrGroup, None)

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--name', dest='name',
            help=_('software profile name'))

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--nodes', action='store_true',
            dest='getNodes', default=False, help=_('get list of nodes'))

        # --packages argument is deprecated
        self.addOptionToGroup(
            softwareProfileAttrGroup, '--packages', action='store_true',
            help=argparse.SUPPRESS)

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--partitions',
            action='store_true', dest='getPartitions', default=False,
            help=_('get list of partitions'))

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--components',
            action='store_true', dest='getComponents', default=False,
            help=_('get list of components'))

        # --os argument is deprecated
        self.addOptionToGroup(
            softwareProfileAttrGroup, '--os', action='store_true',
            help=argparse.SUPPRESS)

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--admins', action='store_true',
            dest='getAdmins', default=False, help=_('get list of admins'))

        outputAttrGroup = _('Output formatting options')

        self.addOptionGroup(outputAttrGroup, None)

        self.addOptionToGroup(
            outputAttrGroup, '--json',
            action='store_true', default=False,
            help=_('JSON formatted output')
        )

        self.addOptionToGroup(
            outputAttrGroup, '--xml',
            action='store_true', default=False,
            help=_('XML formatted output')
        )

        super(GetSoftwareProfileCli, self).parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
    get-software-profile --name=NAME [--nodes --packages
       --partitions --components --os --admins]

Description:
    The get-software-profile tool displays information details of  a  spe-
    cific software profile."""))

        if not self.getArgs().name:
            self.getParser().error('--software-profile must be specified')

        self.swprofileapi = getSoftwareProfileApi(
            self.getUsername(), self.getPassword())

        self.hwprofileapi = getHardwareProfileApi(
            self.getUsername(), self.getPassword())

        optionDict = {}

        if self.getArgs().getNodes:
            optionDict['nodes'] = True

        if self.getArgs().getPartitions:
            optionDict['partitions'] = True

        if self.getArgs().getComponents:
            optionDict['components'] = True

        if self.getArgs().getAdmins:
            optionDict['admins'] = True

        swprofile = self.swprofileapi.getSoftwareProfile(
            self.getArgs().name, optionDict)

        if self.getArgs().json:
            print((json.dumps({
                'swprofile': swprofile.getCleanDict(),
            }, sort_keys=True, indent=4, separators=(',', ': '))))
        elif self.getArgs().xml:
            print(swprofile.getXmlRep())
        else:
            self.__console_output(swprofile)

    def __console_output(self, swprofile):
        hwprofiles = []

        for hwprofilename in \
                [hwprofile_.getName()
                 for hwprofile_ in
                 swprofile.getUsableHardwareProfiles()]:
            hwprofile = self.hwprofileapi.getHardwareProfile(
                hwprofilename, {'resourceadapter': True})

            hwprofiles.append(hwprofile)

        print(swprofile.getName())

        print('  - Description: {0}'.format(swprofile.getDescription()))

        buf = swprofile.getType()

        if swprofile.getType() == 'compute':
            if swprofile.getIsIdle():
                buf += ' (idle software profile)'

        print('  - Type: {0}'.format(buf))

        if self.getArgs().getNodes:

            if swprofile.getNodes():
                print('  - Node(s):')

                for node in swprofile.getNodes():
                    node_entry = node.getName()

                    if node.getNics():
                        node_entry += ' ({0})'.format(
                            ', '.join([nic.getIp() for nic in node.getNics()]))

                    print('    - {0}'.format(node_entry))
            else:
                print('  - Node(s): (none)')

        if self.getArgs().getComponents:
            if swprofile.getComponents():
                print('  - Component(s):')

                for component in swprofile.getComponents():
                    comp_entry = component.getName()

                    print('    - {0}'.format(comp_entry))

        if hwprofiles:
            print('  - Hardware profile(s):')

            for hwprofile in hwprofiles:
                buf = hwprofile.getName()

                if hwprofile.getResourceAdapter() and \
                        hwprofile.getResourceAdapter().getName() == 'default':
                    buf += ' (Type: physical, OS: {0})'.format(
                        swprofile.getOsInfo())
                else:
                    if hwprofile.getResourceAdapter():
                        buf += ' (Type: {0})'.format(
                            hwprofile.getResourceAdapter().getName())

                print('    - {0}'.format(buf))

                if self.getArgs().getPartitions and \
                        swprofile.getPartitions() and \
                        hwprofile.getResourceAdapter() and \
                        hwprofile.getResourceAdapter().getName() == 'default':
                    print('      - Partition(s):')

                    for partition in swprofile.getPartitions():
                        if partition.getFsType() == 'swap':
                            if not partition.getSize():
                                part_size = '<default>'
                            else:
                                part_size = partition.getSize()
                        else:
                            part_size = '{0}'.format(
                                '<grow>' if partition.getGrow() else
                                partition.getSize())

                            if partition.getMaxSize():
                                part_size += ' (Max: {0})'.format(
                                    partition.getMaxSize())

                        if partition.getFsType() == 'swap':
                            device_label = '{0} (swap)'.format(
                                partition.getDevice())
                        else:
                            if partition.getMountPoint():
                                device_label = '{0} ({1})'.format(
                                    partition.getDevice(),
                                    partition.getMountPoint())

                        if partition.getFsType() == 'swap':
                            buf = '{0}: Size: {1}'.format(
                                device_label, part_size)
                        else:
                            buf = '{0}: Name: {1}, Type: {2}, Size: {3}'.\
                                format(
                                    device_label, partition.getName(),
                                    partition.getFsType(), part_size)

                        print(' ' * 8 + '- {0}'.format(buf))
        else:
            print('  - Hardware profile(s): (none)')

        if self.getArgs().getAdmins:
            if swprofile.getAdmins():
                print(' ' * 2 + '- Admins:')

                for admin in swprofile.getAdmins():
                    print(' ' * 4 + '- {0}'.format(admin.getUsername()))
            else:
                print(' ' * 2 + '- Admins: (none)')

        if swprofile.getTags():
            print('  - Tags:')
            for tag_key, tag_value in list(swprofile.getTags().items()):
                print('    - {0}={1}'.format(tag_key, tag_value))
        else:
            print('  - Tags: (none)')


if __name__ == '__main__':
    GetSoftwareProfileCli().run()
