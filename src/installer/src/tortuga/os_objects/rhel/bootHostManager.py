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

import os
import subprocess
from textwrap import dedent

from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.osNotSupported import OsNotSupported
from tortuga.objects.osFamilyInfo import OsFamilyInfo
from tortuga.os_objects.osBootHostManagerCommon import OsBootHostManagerCommon
from tortuga.resourceAdapter.utility import get_provisioning_nic
from tortuga.utility.bootParameters import getBootParameters


class BootHostManager(OsBootHostManagerCommon):
    """
    Methods for manipulating PXE files
    """

    def __getPxelinuxBootFilePath(self, mac):
        pxeconfigDir = os.path.join(self.getTftproot(), 'tortuga/pxelinux.cfg')

        return os.path.join(
            pxeconfigDir, '01-%s' % (mac.replace(':', '-')))

    def __get_kickstart_file_path(self, node: Node):
        return os.path.join(self._cm.getKickstartsDir(), node.name + '.ks')

    def __getPXEFiles(self, dbNode):
        '''
        Returns a list of fully-qualified paths to the PXE file(s)
        associated with the given nodename.
        '''

        try:
            # Find the first nic marked as bootable
            nic = get_provisioning_nic(dbNode)

            if not nic.mac:
                return []

            return [
                self.__getPxelinuxBootFilePath(nic.mac),
                self.__get_kickstart_file_path(dbNode)
            ]
        except NicNotFound:
            return []

    def rmPXEFile(self, dbNode):
        '''
        Remove any/all PXE file(s) associated with the given nodename.
        '''

        for filename in self.__getPXEFiles(dbNode):
            try:
                # Prevent an error in the log file by checking for the
                # file's existence before removing
                if os.path.exists(filename):
                    os.remove(filename)

                self.getLogger().debug(
                    "Removed [%s] for node [%s]" % (filename, dbNode.name))
            except Exception as msg:  # noqa pylint: disable=broad-except
                self.getLogger().debug(
                    "Can't remove [%s] for node [%s]; [%s]" % (
                        filename, dbNode.name, msg))

        # Call OS-specific cleanup routine
        self.deleteNodeCleanup(dbNode)

    def deleteNodeCleanup(self, node):
        if not node.softwareprofile:
            self.getLogger().debug(
                'deleteNodeCleanup(): node [%s] has no associated'
                ' software profile' % (node.name))

            return

        self.getLogger().debug(
            'deleteNodeCleanup(): node=[%s]' % (node.name))

        self.__get_ossupport(node.softwareprofile).deleteNodeCleanup(node)

    def writePXEFile(self, node, localboot=None, hardwareprofile=None,
                     softwareprofile=None):
        # 'hardwareProfile', 'softwareProfile', and 'localboot' are
        # overrides.  If not specified, node.hardwareprofile,
        # node.softwareprofile, and node.bootFrom values are used
        # respectively.

        hwprofile = hardwareprofile if hardwareprofile else \
            node.hardwareprofile

        swprofile = softwareprofile if softwareprofile else \
            node.softwareprofile

        localboot = bool(localboot) \
            if localboot is not None else bool(node.bootFrom)

        self.getLogger().debug(
            'writePXEFile(): node=[%s], hwprofile=[%s],'
            ' swprofile=[%s], localboot=[%s]' % (
                node.name, hwprofile.name, swprofile.name, localboot))

        provisioningNics = hwprofile.nics

        osFamilyInfo = swprofile.os.family

        # Find the first nic marked as bootable
        try:
            nic = get_provisioning_nic(node)
        except NicNotFound:
            # Node does not have a nic marked as bootable.
            return

        result = "# PXE boot configuration for %s\n" % (node.name)

        if localboot:
            result += """
default localdisk
prompt 0
label localdisk
"""

            # Use a sane default
            localBootParams = hwprofile.localBootParams \
                if hwprofile.localBootParams else \
                "kernel chain.c32;append hd0"

            for localBootParam in localBootParams.split(';'):
                result += "    %s\n" % (localBootParam)
        else:
            result += """\
default Reinstall
prompt 0

label Reinstall
"""

            installerIp = provisioningNics[0].ip

            if hwprofile.installType == 'package':
                # Default pxelinux.cfg for package-based installations

                # Find the best IP address to use
                ksurl = 'http://%s:%d/kickstarts/%s' % (
                    installerIp, self._cm.getIntWebPort(),
                    node.name + '.ks')

                # Call the external support module
                try:
                    osSupport = __import__(
                        'tortuga.os.%s.osSupport' % (osFamilyInfo.name),
                        globals(), locals(), ['osSupport'], 0)

                    if not hasattr(osSupport, 'OSSupport'):
                        self.getLogger().error(
                            'Invalid OS support module for [%s]' % (
                                osFamilyInfo.name))

                        return

                    result += osSupport.OSSupport(
                        osFamilyInfo).getPXEReinstallSnippet(
                            ksurl, node, hardwareprofile=hwprofile,
                            softwareprofile=swprofile) + '\n'
                except ImportError:
                    self.getLogger().warning(
                        'OS support module not found for [%s]' % (
                            osFamilyInfo.name))
            else:
                bootParams = getBootParameters(hwprofile, swprofile)

                result += '''    kernel %s
    append initrd=%s hostname=%s %s''' % (bootParams['kernel'],
                                          bootParams['initrd'],
                                          node.name,
                                          bootParams['kernelParams'])

        # Write file contents
        filename = self.__getPxelinuxBootFilePath(nic.mac)

        current_euid = os.geteuid()
        current_egid = os.getegid()

        try:
            # The PXE file needs to be owned by the 'apache' user, so the
            # WS API can update it.
            os.setegid(self.passdata.pw_gid)
            os.seteuid(self.passdata.pw_uid)

            fp = os.open(
                filename, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o644)

            os.write(fp, result.encode())

            os.close(fp)
        finally:
            os.seteuid(current_euid)
            os.setegid(current_egid)

        if hwprofile.installType == 'package':
            # Now write out the kickstart file
            self._writeKickstartFile(node, hwprofile, swprofile)

        # Write 'cloud-init' configuration

        self.write_other_boot_files(node, hwprofile, swprofile)

    def _writeKickstartFile(self, node: Node, hardwareprofile: HardwareProfile,
                            softwareprofile: SoftwareProfile):
        """
        Generate kickstart file for specified node

        Raises:
            OsNotSupported
        """
        osFamilyName = softwareprofile.os.family.name

        try:
            osSupportModule = __import__(
                'tortuga.os.%s.osSupport' % (osFamilyName),
                fromlist=['OSSupport'])
        except ImportError:
            raise OsNotSupported(
                'Operating system family [%s] not supported' % (
                    osFamilyName))

        OSSupport = osSupportModule.OSSupport

        tmpOsFamilyInfo = OsFamilyInfo(
            softwareprofile.os.family.name,
            softwareprofile.os.family.version,
            softwareprofile.os.family.arch)

        contents = OSSupport(tmpOsFamilyInfo).getKickstartFileContents(
            node, hardwareprofile, softwareprofile)

        with open(self.__get_kickstart_file_path(node), 'w') as fp:
            fp.write(contents)

    def _getDhcpNodeName(self, node, nic): \
            # pylint: disable=unused-argument,no-self-use
        return node.name

    def addDhcpLease(self, node, nic) -> None:
        self.getLogger().debug(
            'Adding DHCP lease for node [%s] MAC [%s]' % (node.name, nic.mac))

        dhcpName = self._getDhcpNodeName(node, nic)

        cmds = dedent("""\
            connect
            new host
            set name = "{name}"
            set hardware-address = {mac}
            set hardware-type = 1
            set ip-address = {ip}
            create
            """)

        cmds = cmds.format(name=dhcpName, mac=nic.mac, ip=nic.ip)

        p = subprocess.Popen(['/usr/bin/omshell'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, encoding='utf-8')

        stdout, _ = p.communicate(cmds)

        if p.poll() != 0:
            self.getLogger().error(
                'Error adding DHCP lease for node [%s] (retval=%d): %s' % (
                    node.name, p.returncode, stdout))

    def removeDhcpLease(self, node) -> None:
        # Find first provisioning NIC
        try:
            nic = get_provisioning_nic(node)
        except NicNotFound:
            return

        self.getLogger().debug(
            'Removing DHCP lease for node [%s] MAC [%s]' % (
                node.name, nic.mac))

        dhcpName = self._getDhcpNodeName(node, nic)

        cmds = dedent("""\
            connect
            new host
            set name = "{name}"
            set hardware-address = {mac}
            set hardware-type = 1
            set ip-address = {ip}
            open
            remove
        """)

        cmds = cmds.format(name=dhcpName, mac=nic.mac, ip=nic.ip)

        p = subprocess.Popen(['/usr/bin/omshell'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, encoding='utf-8')

        stdout, _ = p.communicate(cmds)

        if p.poll() != 0:
            self.getLogger().error(
                'Error removing DHCP lease for node [%s] (retval=%d): %s' % (
                    node.name, p.returncode, stdout))

    def getTftproot(self): \
            # pylint: disable=no-self-use
        """
        Returns tftpboot root directory
        """

        return '/var/lib/tftpboot'

    def __get_ossupport_module(self, osFamilyName): \
            # pylint: disable=no-self-use
        """
        Raises:
            OsNotSupported
        """

        try:
            return __import__(
                'tortuga.os.%s.osSupport' % (osFamilyName),
                fromlist=['OSSupport']).OSSupport
        except ImportError:
            raise OsNotSupported(
                'Operating system family [%s] not supported' % (
                    osFamilyName))

    def __get_ossupport(self, softwareprofile):
        OSSupport = self.__get_ossupport_module(
            softwareprofile.os.family.name)

        tmpOsFamilyInfo = OsFamilyInfo(
            softwareprofile.os.family.name,
            softwareprofile.os.family.version,
            softwareprofile.os.family.arch)

        return OSSupport(tmpOsFamilyInfo)

    def get_cloud_config(self, node, hardwareprofile=None,
                         softwareprofile=None):
        '''
        Returns cloud-init compatible cloud config in 'dict'. This *must*
        be converted to YAML to be used by cloud providers!
        '''

        self.getLogger().debug(
            'get_cloud_config(): node=[%s], hardwareprofile=[%s],'
            ' softwareprofile=[%s]' % (
                node.name,
                hardwareprofile.name if hardwareprofile else '(None)',
                softwareprofile.name if softwareprofile else '(None)'))

        hardwareprofile = hardwareprofile \
            if hardwareprofile else node.hardwareprofile

        softwareprofile = softwareprofile \
            if softwareprofile else node.softwareprofile

        return self.__get_ossupport(softwareprofile).get_cloud_config(
            node, hardwareprofile, softwareprofile)

    def write_other_boot_files(self, node, hardwareprofile, softwareprofile):
        if not hardwareprofile:
            hardwareprofile = node.hardwareprofile

        if not softwareprofile:
            softwareprofile = node.softwareprofile

        self.getLogger().debug(
            'write_other_boot_files(): node=[%s], hardwareprofile=[%s],'
            ' softwareprofile=[%s]' % (
                node.name,
                hardwareprofile.name,
                softwareprofile.name if softwareprofile else '(None)'))

        self.__get_ossupport(softwareprofile).write_other_boot_files(
            node, hardwareprofile, softwareprofile)
