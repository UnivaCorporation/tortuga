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
from typing import Optional

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class GetSoftwareProfileCli(TortugaCli):
    """
    Get software profile command line interface.
    """

    def parseArgs(self, usage: Optional[str] = None):
        softwareProfileAttrGroup = _('Software Profile Attribute Options')

        self.addOptionGroup(softwareProfileAttrGroup, None)

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--name', dest='deprecated_name',
            help=argparse.SUPPRESS)

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

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--data-root', action='store_true',
            dest='getDataRoot', default=False, help=_('get root directories for user data'))

        self.addOptionToGroup(
            softwareProfileAttrGroup, '--data-rsync', action='store_true',
            dest='getDataRsync', default=False, help=_('get rsync configuration'))

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
            help=argparse.SUPPRESS
        )

        self.getParser().add_argument(
            'name', metavar='NAME', nargs='?',
            help=_('software profile name')
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(usage=_('Displays software profile details'))

        if not self.getArgs().name and not self.getArgs().deprecated_name:
            self.getParser().error(
                'the following arguments are required: NAME'
            )

        if self.getArgs().name and self.getArgs().deprecated_name:
            self.getParser().error(
                'argument name: not allowed with argument --name'
            )

        name = self.getArgs().name \
            if self.getArgs().name else self.getArgs().deprecated_name

        swprofileapi = SoftwareProfileWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl(),
            verify=self._verify)

        optionDict = {}

        if self.getArgs().getNodes:
            optionDict['nodes'] = True

        if self.getArgs().getPartitions:
            optionDict['partitions'] = True

        if self.getArgs().getComponents:
            optionDict['components'] = True

        if self.getArgs().getAdmins:
            optionDict['admins'] = True

        if self.getArgs().getDataRoot:
            optionDict['dataRoot'] = True

        if self.getArgs().getDataRoot:
            optionDict['dataRsync'] = True

        swprofile = swprofileapi.getSoftwareProfile(name, optionDict)

        if self.getArgs().json:
            print(json.dumps({
                'softwareprofile': swprofile.getCleanDict(),
            }, sort_keys=True, indent=4, separators=(',', ': ')))
        elif self.getArgs().xml:
            print(swprofile.getXmlRep())
        else:
            self.__console_output(swprofile)

    def __console_output(self, swprofile):
        hwprofiles = []

        hwprofileapi = HardwareProfileWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl(),
            verify=self._verify)

        for hwprofilename in \
                [hwprofile_.getName()
                 for hwprofile_ in
                 swprofile.getUsableHardwareProfiles()]:
            hwprofile = hwprofileapi.getHardwareProfile(
                hwprofilename, {'resourceadapter': True})

            hwprofiles.append(hwprofile)

        print(swprofile.getName())

        print('  - Description: {0}'.format(swprofile.getDescription()))

        print('  - State: {}'.format(swprofile.getLockedState()))

        print('  - Min nodes: {}, max nodes: {}'.format(
            swprofile.getMinNodes()
            if swprofile.getMinNodes() != -1 else '<NONE>',
            swprofile.getMaxNodes()
            if swprofile.getMaxNodes() != -1 else '<NONE>'))

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

                        device_label = None

                        if partition.getFsType() == 'swap':
                            device_label = '{0} (swap)'.format(
                                partition.getDevice())
                        elif partition.getMountPoint():
                                device_label = '{0} ({1})'.format(
                                    partition.getDevice(),
                                    partition.getMountPoint())
                        else:
                            device_label = '<no mountpoint>'

                        if partition.getFsType() == 'swap':
                            buf = '{0}: Size: {1}'.format(
                                device_label, part_size)
                        else:
                            buf = ('{0}: Name: {1}, Type: {2},'
                                   ' Size: {3}'.format(
                                       device_label,
                                       partition.getName(),
                                       partition.getFsType(),
                                       part_size))

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

        if self.getArgs().getDataRoot:
            if swprofile.getDataRoot():
                print('  - Data Roots: {0}'.format(swprofile.getDataRoot()))
            else:
                print('  - Data Roots: (none)')

        if self.getArgs().getDataRync:
            if swprofile.getDataRsync():
                print('  - Rsync config: {0}'.format(swprofile.getDataRsync()))
            else:
                print('  - Rsync config: (none)')


def main():
    GetSoftwareProfileCli().run()


if __name__ == '__main__':
    main()
