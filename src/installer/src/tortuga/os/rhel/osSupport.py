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

import crypt
import os.path
import socket
import string
import time
from random import choice
from typing import Any, Dict, List, NoReturn, Optional, Union

from jinja2 import Template

from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.db.helper import get_installer_hostname_suffix
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.partition import Partition
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.os.osSupportBase import OsSupportBase
from tortuga.utility.bootParameters import getBootParameters


def sort_by_devicename_comparator(nic1: Nic, nic2: Nic) -> int:
    if nic1.networkdevice is None and nic2.networkdevice is None:
        return 0

    if nic1.networkdevice is None:
        return -1

    if nic2.networkdevice is None:
        return 1

    if nic1.networkdevice.name < nic2.networkdevice.name:
        return -1

    if nic1.networkdevice.name > nic2.networkdevice.name:
        return 1

    return 0


class OSSupport(OsSupportBase):
    def __init__(self, osFamilyInfo):
        super(OSSupport, self).__init__(osFamilyInfo)

        self._globalParameterDbApi = GlobalParameterDbApi()

        try:
            depot_dir = \
                self._globalParameterDbApi.getParameter('depot').getValue()
        except ParameterNotFound:
            # Fallback to legacy default
            depot_dir = '/opt/tortuga/depot'

        self._cm.setDepotDir(depot_dir)

    def getPXEReinstallSnippet(self, ksurl: str, node: Node,
                               hardwareprofile: Optional[Union[HardwareProfile, None]] = None,
                               softwareprofile: Optional[Union[SoftwareProfile, None]] = None) -> str: \
            # pylint: disable=no-self-use
        # General kickstart/kernel parameters

        # Find the first nic marked as bootable
        nics = [nic for nic in node.nics if nic.boot]

        if not nics:
            raise NicNotFound(
                'Node [%s] does not have a bootable NIC' % (node.name))

        # Choose the first one
        nic = nics[0]

        if hardwareprofile is None:
            hardwareprofile = node.hardwareprofile

        if softwareprofile is None:
            softwareprofile = node.softwareprofile

        # Use settings from software profile, if defined, otherwise use
        # settings from hardware profile.
        bootParams = getBootParameters(hardwareprofile, softwareprofile)

        kernel = bootParams['kernel']
        kernelParams = bootParams['kernelParams']
        initrd = bootParams['initrd']

        bootargs = [
        ]

        if softwareprofile.os.family.version == '7':
            # RHEL 7.x
            bootargs.append(
                'inst.ks=%s ip=%s:dhcp' % (ksurl, nic.networkdevice.name))
        else:
            # RHEL 5.x and 6.x
            bootargs.append('ks=%s' % (ksurl))

            bootargs.append('ksdevice=%s' % (nic.networkdevice.name))

        # Append kernel parameters, if defined.
        if kernelParams:
            bootargs.append(kernelParams)

        result = '''\
    kernel %s
    append initrd=%s %s''' % (kernel, initrd, ' '.join(bootargs))

        return result

    def __get_kickstart_network_entry(self, dbNode: None,
                                      hardwareprofile: HardwareProfile,
                                      nic: Nic) -> str: \
            # pylint: disable=no-self-use
        bProvisioningNic = nic.network == hardwareprofile.nics[0].network

        installer_private_ip = hardwareprofile.nics[0].ip

        if not bProvisioningNic and not nic.network.usingDhcp and not nic.ip:
            # Unconfigured public static IP network
            return None

        bActivate = False

        # By default, all interfaces are enabled at on boot
        bOnBoot = True

        # Use the network device name, as specified in the hardware profile
        netargs = [
            'network --device %s' % (nic.networkdevice.name)
        ]

        if bProvisioningNic:
            netargs.append(
                '--bootproto %s' % (
                    'static' if bProvisioningNic or
                    not nic.network.usingDhcp else 'dhcp'))

            netargs.append('--ip=%s' % (nic.ip))
            netargs.append('--netmask=%s' % (nic.network.netmask))
            netargs.append('--nameserver=%s' % (installer_private_ip))

            bActivate = True
        else:
            if nic.network and nic.network.usingDhcp:
                netargs.append('--bootproto dhcp')
            else:
                netargs.append('--bootproto static')

                if nic.ip:
                    netargs.append('--ip=%s' % (nic.ip))
                    netargs.append('--netmask=%s' % (nic.network.netmask))
                else:
                    # Do not enable interface if it's not configured
                    netargs.append('--onboot=no')

                    bOnBoot = False

        # Store provisioning network interface device name for
        # later reference in the template

        # Ensure all interfaces are activated
        if bActivate:
            netargs.append('--activate')

        bDefaultRoute = True

        if bProvisioningNic:
            # This is the nic connected to the provisioning network.

            if len(dbNode.nics) > 1:
                # Disable the default route on the management network.
                netargs.append('--nodefroute')

                bDefaultRoute = False
        else:
            # Disable DNS for all interfaces other than the
            # provisioning network
            if bOnBoot:
                netargs.append('--nodns')

        if nic.network.gateway and bDefaultRoute:
            netargs.append('--gateway %s' % (nic.network.gateway))

        return ' '.join(netargs)

    def __validate_node(self, node: Node) -> NoReturn: \
            # pylint: disable=no-self-use
        """
        Raises:
            NodeNotFound
            NicNotFound
        """

        if not node.name:
            raise NodeNotFound('Node must have a name')

        if not node.nics:
            raise NicNotFound('Node [%s] has no associated nics' % (
                node.name))

    def __kickstart_get_timezone(self) -> str:
        tz = self._globalParameterDbApi.getParameter(
            'Timezone_zone').getValue()

        # Ensure timezone does not contain any spaces
        return tz.replace(' ', '_')

    def __kickstart_get_network_section(self, node: Node,
                                        hardwareprofile: HardwareProfile) -> str:
        # Ensure nics are processed in order (ie. eth0, eth1, eth2...)
        nics = node.nics
        nics.sort(key=lambda nic: nic.networkdevice.name)

        network_entries = []
        hostname_set = False

        # Iterate over nics, adding 'network' Kickstart entries for each
        for nic in nics:
            networkString = self.__get_kickstart_network_entry(
                node, hardwareprofile, nic)

            if not networkString:
                continue

            if not hostname_set and nic.boot and \
                    nic.network.type == 'provision':
                networkString += ' --hostname=%s' % (node.name)

                hostname_set = True

            network_entries.append(networkString)

        return '\n'.join(network_entries)

    def __kickstart_get_repos(self, dbSwProfile: SoftwareProfile,
                              installer_private_ip: str) -> List[str]:
        repo_entries = []

        for dbComponent in dbSwProfile.components:
            dbKit = dbComponent.kit
            if dbKit.isOs or dbKit.name != 'base':
                # Do not add repos for OS kits
                continue

            kitVer = '%s-%s' % (dbKit.version, dbKit.iteration)
            kitArch = 'noarch'

            subpath = '%s/%s/%s' % (dbKit.name, kitVer, kitArch)

            # Check if repository actually exists
            if not os.path.exists(os.path.join(self._cm.getDepotDir(),
                                               'kits',
                                               subpath,
                                               'repodata',
                                               'repomd.xml')):
                # Repository for specified kit is empty. Nothing to do...
                continue

            url = self._cm.getYumRootUrl(installer_private_ip) + \
                '/' + subpath

            repo_entries.append(
                'repo --name %s --baseurl=%s' % (dbKit.name, url))

        subpath = '3rdparty/%s/%s/%s' % (dbSwProfile.os.family.name,
                                         dbSwProfile.os.family.version,
                                         dbSwProfile.os.arch)

        if os.path.exists(os.path.join(self._cm.getRoot(),
                                       'repos',
                                       subpath,
                                       'repodata/repomd.xml')):
            # Third-party repository contains packages, include it in
            # Kickstart
            url = '%s/%s' % (
                self._cm.getYumRootUrl(installer_private_ip), subpath)

            repo_entries.append(
                'repo --name tortuga-third-party --baseurl=%s' % (url))

        return repo_entries

    def __get_kickstart_template(self, swprofile: SoftwareProfile) -> str:
        ksTemplate = os.path.join(
            self._cm.getKitConfigBase(),
            'kickstart-%s.tmpl' % (swprofile.os.family.name.encode('ascii')))

        if not os.path.exists(ksTemplate):
            ksTemplate = os.path.join(
                self._cm.getKitConfigBase(),
                'kickstart-%s.tmpl' % (swprofile.name.encode('ascii')))

            if not os.path.exists(ksTemplate):
                ksTemplate = os.path.join(
                    self._cm.getKitConfigBase(), 'kickstart.tmpl')

        return ksTemplate

    def __kickstart_get_partition_section(self,
                                          softwareprofile: SoftwareProfile) -> str:
        buf = """\
#!/bin/sh
# Determine how many drives we have
"""

        # Temporary workaround for RHEL 5.7 based distros
        # https://bugzilla.redhat.com/show_bug.cgi?format=multiple&id=709880
        if softwareprofile.os.version == '5.7':
            buf += 'set $(PYTHONPATH=/usr/lib/booty list-harddrives)\n'
        else:
            buf += 'set $(list-harddrives)\n'

        buf += """
d1=$1
d2=$3
d3=$5
d4=$7
"""

        clearpartstr = '''
cat >/tmp/partinfo << __PARTINFO__
zerombr
'''

        disksToPreserve = []

        # Need to get the drives to clear
        clearpartstr += 'clearpart '
        driveNumbers = []

        for dbPartition in softwareprofile.partitions:
            disk = dbPartition.device.split('.')[0]

            if disk not in driveNumbers:
                driveNumbers.append(disk)

                if not dbPartition.preserve:
                    # This is a partition to clear
                    if len(driveNumbers) == 1:
                        # First drive
                        clearpartstr += ('--all --initlabel'
                                         ' --drives="${d%s:-nodisk}' % (
                                             disk))
                    else:
                        clearpartstr += ',${d%s:-nodisk}' % (disk)
                else:
                    disksToPreserve.append(disk)

        clearpartstr += "--none" if not driveNumbers else '"'
        clearpartstr += '\n'

        for diskNum in driveNumbers:
            if diskNum in disksToPreserve:
                continue

            buf += '''
dd if=/dev/zero of=$d%s bs=512 count=1
''' % (diskNum)

        buf += clearpartstr

        bootloaderLocation = "mbr"

        # Now create partitions
        for dbPartition in softwareprofile.partitions:
            if dbPartition.bootLoader:
                # Can't control the partition in anaconda...it will be on
                # the drive with the boot partition
                bootloaderLocation = 'partition'

            buf += self._processPartition(dbPartition)

        # now do the bootloader
        buf += (
            'bootloader --location=%s --driveorder=${d1:-nodisk}\n' % (
                bootloaderLocation))

        buf += '__PARTINFO__\n'

        return buf

    def __get_template_subst_dict(self, node: Node,
                                  hardwareprofile: HardwareProfile,
                                  softwareprofile: SoftwareProfile) -> Dict[str, Any]:
        """
        :param node: Object
        :param hardwareprofile: Object
        :param softwareprofile: Object
        :return: Dictionary
        """
        hardwareprofile = hardwareprofile \
            if hardwareprofile else node.hardwareprofile
        softwareprofile = softwareprofile \
            if softwareprofile else node.softwareprofile

        installer_public_fqdn: str = socket.getfqdn()
        installer_hostname: str = installer_public_fqdn.split('.')[0]

        installer_private_ip: str = hardwareprofile.nics[0].ip

        try:
            private_domain: Optional[str] = self._globalParameterDbApi.\
                getParameter('DNSZone').getValue()
        except ParameterNotFound:
            private_domain: Optional[str] = None

        installer_private_fqdn: str = '%s%s%s' % (
            installer_hostname,
            get_installer_hostname_suffix(
                hardwareprofile.nics[0], enable_interface_aliases=None),
            '.%s' % private_domain if private_domain else '')

        values: List[str] = node.name.split('.', 1)
        domain: str = values[1].lower() if len(values) == 2 else ''

        return {
            'fqdn': node.name,
            'domain': domain,
            'hostname': installer_hostname,
            'installer_private_fqdn': installer_private_fqdn,
            'installer_private_domain': private_domain,
            'installer_private_ip': installer_private_ip,
            'puppet_master_fqdn': installer_public_fqdn,
            'installer_public_fqdn': installer_public_fqdn,
            'ntpserver': installer_private_ip,
            'os': softwareprofile.os.name,
            'osfamily': softwareprofile.os.family.name,
            'osfamilyvers': int(softwareprofile.os.family.version),
            # These are deprecated and included for backwards compatibility
            # only. Do not reference them in any new kickstart templates.
            'primaryinstaller': installer_private_fqdn,
            'puppetserver': installer_public_fqdn,
            'installerip': installer_private_ip,
            # Add entry for install package source
            'url': '%s/%s/%s/%s' % (
                self._cm.getYumRootUrl(installer_private_fqdn),
                softwareprofile.os.name,
                softwareprofile.os.version,
                softwareprofile.os.arch
            ),
            'lang': 'en_US.UTF-8',
            'keyboard': 'us',
            'networkcfg': self.__kickstart_get_network_section(
                node, hardwareprofile
            ),
            'rootpw': self._generatePassword(),
            'timezone': self.__kickstart_get_timezone(),
            'includes': '%include /tmp/partinfo',
            'repos': '\n'.join(
                self.__kickstart_get_repos(
                    softwareprofile,
                    installer_private_fqdn
                )
            ),
            # Retain this for backwards compatibility with legacy Kickstart
            # templates
            'packages': '\n'.join([]),
            'prescript': self.__kickstart_get_partition_section(
                softwareprofile
            ),
            'installer_url': self._cm.getInstallerUrl(installer_private_fqdn),
            'cfmstring': self._cm.getCfmPassword()
        }

    def getKickstartFileContents(self, node: Node,
                                 hardwareprofile: HardwareProfile,
                                 softwareprofile: SoftwareProfile) -> str:
        # Perform basic sanity checking before proceeding
        self.__validate_node(node)

        template_subst_dict = self.__get_template_subst_dict(
            node, hardwareprofile, softwareprofile)

        with open(self.__get_kickstart_template(softwareprofile)) as fp:
            tmpl = fp.read()

        return Template(tmpl).render(template_subst_dict)

    @staticmethod
    def _generatePassword() -> str:
        string_length: int = 8
        string_characters: str = string.ascii_letters + string.digits
        root_password: str = ''.join([choice(string_characters) for _ in range(string_length)])
        root_password_salted: str = crypt.crypt(str(root_password), str(time.time()))
        return root_password_salted

    def __get_partition_mountpoint(self, dbPartition: Partition) -> str: \
            # pylint: disable=no-self-use
        if not dbPartition.mountPoint:
            if dbPartition.fsType == 'swap':
                mountPoint = 'swap'
            else:
                # Any partition that does not have a mountpoint defined
                # is ignored.
                return None
        else:
            mountPoint = dbPartition.mountPoint

        return mountPoint

    def _processPartition(self, dbPartition: Partition) -> str: \
            # pylint: disable=no-self-use
        mountPoint = dbPartition.mountPoint \
            if dbPartition.mountPoint else \
            self.__get_partition_mountpoint(dbPartition)

        if not mountPoint:
            return ''

        # All partitions must have a mount point and partition type
        result = 'part %s --fstype %s' % (mountPoint, dbPartition.fsType)

        # This will throw an exception if the size stored in the
        # partition settings is not an integer.
        if dbPartition.size:
            result += ' --size=%d' % (dbPartition.size)
        else:
            # If partition size is not set or is zero, use '--recommended' flag
            if mountPoint == 'swap':
                result += ' --recommended'

        disk, part = dbPartition.device.split('.')

        optionsList = dbPartition.options.split(',') \
            if dbPartition.options else []

        if dbPartition.grow is not None:
            result += ' --grow'

            if dbPartition.maxSize is not None:
                result += ' --maxsize %d' % (dbPartition.maxSize)

        if optionsList:
            # Add the fs options...
            result += ' --fsoptions="%s"' % (','.join(optionsList))

        result += ' --noformat --onpart=${d%s:-nodisk}%s' % (disk, part) \
            if dbPartition.preserve else \
            ' --ondisk=${d%s:-nodisk}' % str(disk)

        result += '\n'

        return result
