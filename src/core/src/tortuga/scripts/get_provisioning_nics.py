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

import sys
import yaml

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi
from tortuga.wsapi.nodeWsApi import NodeWsApi


class GetProvisioningNicsApp(TortugaCli):
    def parseArgs(self, usage=None):
        self.addOption('--hardware-profile', dest='hardwareProfile',
                       help=('Return provisioning NIC for specified'
                             'hardware profile'))

        self.addOption('--yaml', dest='bYaml', action='store_true',
                       default=False, help='Output in YAML')

        self.addOption('--verbose', dest='bVerbose', action='store_true',
                       default=False, help='Enable verbose mode')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        if self.getArgs().hardwareProfile:
            hw_profile_api = HardwareProfileWsApi(username=self.getUsername(),
                                                  password=self.getPassword(),
                                                  baseurl=self.getUrl(),
                                                  verify=self._verify)

            hw_profile = hw_profile_api.getHardwareProfile(
                self.getArgs().hardwareProfile, {
                    'hardwareprofilenetworks': True
                })

            if not hw_profile.getProvisioningNics():
                print(yaml.dump({}))

                sys.exit(0)

            nic = hw_profile.getProvisioningNics()[0]

            data_dict = {
                'device': nic.getNetworkDevice().getName(),
                'ip': nic.getIp(),
                'network': {
                    'address': nic.getNetwork().getAddress(),
                    'netmask': nic.getNetwork().getNetmask()
                }
            }

            if self.getArgs().bVerbose:
                print(yaml.safe_dump(data_dict))
            else:
                print(yaml.safe_dump(nic.getNetworkDevice().getName()))
        else:
            # Display list of provisioning NICs on installer
            node_api = NodeWsApi(username=self.getUsername(),
                                 password=self.getPassword(),
                                 baseurl=self.getUrl(),
                                 verify=self._verify)

            data_dict = {}

            for nic in node_api.getInstallerNode().getNics():
                if nic.getNetwork().getType() != 'provision':
                    continue

                device_name = nic.getNetworkDevice().getName()

                data_dict[device_name] = {}

                if self.getArgs().bVerbose:
                    data_dict[device_name] = {
                        'ip': nic.getIp(),
                        'network': {
                            'address': nic.getNetwork().getAddress(),
                            'netmask': nic.getNetwork().getNetmask()
                        }
                    }

            if self.getArgs().bVerbose:
                print(yaml.safe_dump(data_dict))
            else:
                print(yaml.safe_dump(list(data_dict.keys())))


if __name__ == '__main__':
    GetProvisioningNicsApp().run()
