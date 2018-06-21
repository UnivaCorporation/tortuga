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
import xml.etree.cElementTree as ET

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.config.configManager import ConfigManager, getfqdn
from tortuga.wsapi.nodeWsApi import NodeWsApi


class GenerateNiiProfileCli(TortugaCli):
    """
    Update node status command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption("--node", dest='nodeName', default=getfqdn(),
                       help='Name of the node for which NII profile is being'
                            ' generated')

        self.addOption("--installer", dest='installer',
                       required=True,
                       help='IP address or hostname (and optional port number)'
                            ' of the installer node')

        self.addOption("--root-mount-point", dest='rootMountPoint',
                       default='/', help='Root file system mount point')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        installer = self.getArgs().installer

        cm = ConfigManager()

        if ':' in installer:
            instHostName, instHostPort = installer.split(':')
        else:
            instHostName = installer
            instHostPort = cm.getAdminPort()

        cm.setInstaller(instHostName)
        cm.setAdminPort(int(instHostPort))

        api = NodeWsApi(username=self.getUsername(),
                        password=self.getPassword(),
                        baseurl=self.getUrl())

        fileContent = api.getProvisioningInfo(
            self.getArgs().nodeName).getXmlRep()

        # Load generated XML and update installer host name value
        dom = ET.fromstring(fileContent)

        # Override the installer host name with that provided on command-line
        if self.getArgs().installer:
            for elem in dom.findall('./globalparameter'):
                if elem.get('name') == 'Installer':
                    elem.set('value', instHostName)

        # Generate file.
        rootMountPoint = self.getArgs().rootMountPoint
        niiProfileFile = ConfigManager().getProfileNiiFile()
        if rootMountPoint != '/':
            niiProfileFile = rootMountPoint + niiProfileFile
            dirPath = os.path.dirname(niiProfileFile)
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)

        with open(niiProfileFile, 'w') as f:
            f.write(ET.tostring(dom, 'UTF-8').decode())


def main():
    GenerateNiiProfileCli().run()
