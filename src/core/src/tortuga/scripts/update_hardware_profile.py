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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.objects.network import Network
from tortuga.objects.networkDevice import NetworkDevice
from tortuga.objects.resourceAdapter import ResourceAdapter
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi
from tortuga.wsapi.nodeWsApi import NodeWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class UpdateHardwareProfileCli(TortugaCli):
    """
    Update tortuga command line interface.
    """

    # Hardware Profile Fetch Options
    # Skip nodes and admins for update operations
    optionDict = {
        'hardwareprofilenetworks': True,
        'resourceadapter': True,
    }

    def parseArgs(self, usage=None):
        # Simple Options
        self.addOption('--name',
                       dest='name', required=True,
                       help=_('Name of hardware profile.'))

        self.addOption('--new-name',
                       dest='newName',
                       help=_('New name for hardware profile.'))

        self.addOption('--description',
                       dest='description',
                       help=_('User description of this hardware profile.'))

        self.addOption('--name-format',
                       dest='nameFormat',
                       help=_('Name format for hardware profile.'))

        self.addOption('--kernel',
                       dest='kernel',
                       help=_('Kernel for hardware profile.'))

        self.addOption('--kernel-parameters',
                       dest='kernelParameters',
                       help=_('Kernel parameters for hardware profile.'))

        self.addOption('--initrd',
                       dest='initrd',
                       help=_('Initrd for hardware profile.'))

        self.addOption('--software-override-allowed',
                       dest='soAllowed',
                       help=_('Allow software profile override of'
                              ' kernel and initrd values.'))

        self.addOption('--idle-software-profile',
                       dest='idleProfile',
                       help=_('Idle software profile.'))

        self.addOption('--unset-idle-software-profile',
                       dest='bUnsetIdleProfile', action='store_true',
                       default=False,
                       help=_('Remove currently idle software profile'
                              ' association'))

        self.addOption('--location',
                       dest='location',
                       help=_('Physical location of nodes in this'
                              ' hardware profile.'))

        self.addOption('--local-boot-parameters',
                       dest='localBootParameters',
                       help=_('Grub configuration contents for member'
                              ' nodes.'))

        self.addOption('--resource-adapter',
                       dest='resourceAdapter',
                       help=_('Tortuga resource adapter.'))

        self.addOption(
            '--default-resource-adapter-configuration-profile',
            '-A',
            dest='default_adapter_config',
            help=_('Default resource adapter configuration profile')
        )

        self.addOption('--add-provisioning-nic',
                       dest='addPNic',
                       action='append',
                       help=_('Provisioning NIC to associate with hardware'
                              ' profile.'))

        self.addOption('--delete-provisioning-nic',
                       dest='deletePNic', action='append',
                       help=_('Provisioning NIC to delete from hardware'
                              ' profile.'))

        self.addOption('--add-network',
                       dest='addNetwork',
                       action='append',
                       help=_('Network to associate with hardware profile.'))

        self.addOption('--delete-network',
                       dest='deleteNetwork', action='append',
                       help=_('Network to delete from hardware profile.'))

        self.addOption(
            '--cost', dest='cost', type=int,
            help=_('Set relative \'cost\' of hardware profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        spApi = SoftwareProfileWsApi(username=self.getUsername(),
                                     password=self.getPassword(),
                                     baseurl=self.getUrl())

        nodeApi = NodeWsApi(username=self.getUsername(),
                            password=self.getPassword(),
                            baseurl=self.getUrl())

        hp = api.getHardwareProfile(self.getArgs().name,
                                    UpdateHardwareProfileCli.optionDict)

        if self.getArgs().newName is not None:
            hp.setName(self.getArgs().newName)

        if self.getArgs().description is not None:
            hp.setDescription(self.getArgs().description)

        if self.getArgs().nameFormat is not None:
            hp.setNameFormat(self.getArgs().nameFormat)

        if self.getArgs().kernel is not None:
            hp.setKernel(self.getArgs().kernel)

        if self.getArgs().kernelParameters is not None:
            hp.setKernelParams(self.getArgs().kernelParameters)

        if self.getArgs().initrd is not None:
            hp.setInitrd(self.getArgs().initrd)

        if self.getArgs().soAllowed is not None:
            if self.getArgs().soAllowed.lower() == _('true'):
                hp.setSoftwareOverrideAllowed(True)
            elif self.getArgs().soAllowed.lower() == _('false'):
                hp.setSoftwareOverrideAllowed(False)
            else:
                raise InvalidCliRequest(
                    _('--software-override-allowed must be either "true" or'
                      ' "false".'))

        if self.getArgs().idleProfile is not None and \
           self.getArgs().bUnsetIdleProfile:
            raise InvalidCliRequest(
                _('Conflicting options --idle-software-profile and'
                  ' --unset-idle-software-profile'))

        if self.getArgs().idleProfile is not None:
            sp = spApi.getSoftwareProfile(self.getArgs().idleProfile)

            hp.setIdleSoftwareProfileId(sp.getId())

        if self.getArgs().bUnsetIdleProfile:
            hp.setIdleSoftwareProfileId(None)

        if self.getArgs().location is not None:
            hp.setLocation(self.getArgs().location)

        if self.getArgs().localBootParameters is not None:
            hp.setLocalBootParams(self.getArgs().localBootParameters)

        if self.getArgs().cost is not None:
            hp.setCost(self.getArgs().cost)

        if self.getArgs().resourceAdapter:
            resourceAdapter = ResourceAdapter(
                name=self.getArgs().resourceAdapter)
            hp.setResourceAdapter(resourceAdapter)

        if self.getArgs().default_adapter_config:
            hp.setDefaultResourceAdapterConfig(
                self.getArgs().default_adapter_config)

        if self.getArgs().deletePNic is not None:
            out = TortugaObjectList()

            for nic in hp.getProvisioningNics():
                for dnic in self.getArgs().deletePNic:
                    if dnic == nic.getIp():
                        # Skip over this item..its getting deleted
                        break
                else:
                    # Not a NIC we are deleting
                    out.append(nic)

            hp.setProvisioningNics(out)

        if self.getArgs().addPNic is not None:
            for nicIp in self.getArgs().addPNic:
                nicsNode = nodeApi.getNodeByIp(nicIp)

                if nicsNode is not None:
                    for nic in nicsNode.getNics():
                        if nic.getIp() == nicIp:
                            hp.getProvisioningNics().append(nic)
                            break

        if self.getArgs().deleteNetwork is not None:
            # Make sure we actually delete a network
            out = TortugaObjectList()
            out.extend(hp.getNetworks())

            for netstring in self.getArgs().deleteNetwork:
                try:
                    dnet, dmask, ddev = netstring.split('/')
                except ValueError:
                    raise InvalidCliRequest(
                        _('Incorrect input format for --delete-network'
                          ' ("address/mask/device")'))

                for network in hp.getNetworks():
                    if dnet == network.getAddress() and \
                       dmask == network.getNetmask() and \
                       ddev == network.getNetworkDevice().getName():
                        # Skip over this item..its getting deleted
                        for n in out:
                            if n.getId() == network.getId():
                                out.remove(n)
                                break

                        break
                else:
                    # Not a NIC we are deleting
                    print('Ignoring deletion of non-existent network:'
                          ' %s/%s/%s' % (dnet, dmask, ddev))

            hp.setNetworks(out)

        if self.getArgs().addNetwork:
            for netstring in self.getArgs().addNetwork:
                try:
                    anet, amask, adev = netstring.split('/')
                except ValueError:
                    raise InvalidCliRequest(
                        _('Incorrect input format for --add-network'
                          ' ("address/mask/device")'))

                network = Network()
                networkDevice = NetworkDevice()
                networkDevice.setName(adev)
                network.setAddress(anet)
                network.setNetmask(amask)
                network.setNetworkDevice(networkDevice)
                hp.getNetworks().append(network)

        api.updateHardwareProfile(hp)


def main():
    UpdateHardwareProfileCli().run()
