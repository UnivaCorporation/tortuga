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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.node.nodeApiFactory import getNodeApi
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.objects.network import Network
from tortuga.objects.networkDevice import NetworkDevice
from tortuga.objects.resourceAdapter import ResourceAdapter
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi
from tortuga.wsapi.networkWsApi import NetworkWsApi
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

    def __init__(self):
        TortugaCli.__init__(self)

        # Simple Options
        self.addOption('--name',
                       dest='name',
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

        self.addOption('--hypervisor-profile',
                       dest='vcProfile',
                       help=_('"Parent" software profile of this hardware'
                              ' profile.'))

        self.addOption('--clear-hypervisor-profile',
                       dest='bClearHypervisorProfile',
                       action='store_true', default=False,
                       help=_('Unset the current hypervisor software'
                              'profile'))

        self.addOption('--max-units',
                       dest='maxUnits',
                       help=_('Maximum number of compute units for node'
                              ' memeber.'))

        self.addOption('--resource-adapter',
                       dest='resourceAdapter',
                       help=_('Tortuga resource adapter.'))

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

        # Or an xml file can be passed in
        self.addOption('--xml-file',
                       dest='xmlFile',
                       help=_('XML file containing representation of a'
                              ' hardware profile.'))

        self.addOption(
            '--cost', dest='cost', type=int,
            help=_('Set the \'cost\' of this hardware profile'))

    def runCommand(self):
        self.parseArgs(_('Update hardware profile configuration'))

        hwProfileName = self.getArgs().name

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        if self.getArgs().xmlFile:
            # An XML file was provided as input...start with that...
            with open(self.getArgs().xmlFile) as f:
                xmlString = f.read()

            try:
                hp = HardwareProfile.getFromXml(xmlString)
            except Exception as ex:
                hp = None
                self.getLogger().debug('Error parsing xml %s' % ex)

            if hp is None:
                raise InvalidCliRequest(
                    _('File "%s" does not contain a valid hardware'
                      ' profile') % (self.getArgs().xmlFile))
        else:
            if hwProfileName is None:
                raise InvalidCliRequest(_('Missing hardware profile name'))

            hp = api.getHardwareProfile(hwProfileName,
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
            spApi = SoftwareProfileWsApi(username=self.getUsername(),
                                         password=self.getPassword(),
                                         baseurl=self.getUrl())

            sp = spApi.getSoftwareProfile(self.getArgs().idleProfile)

            hp.setIdleSoftwareProfileId(sp.getId())

        if self.getArgs().bUnsetIdleProfile:
            hp.setIdleSoftwareProfileId(None)

        if self.getArgs().location is not None:
            hp.setLocation(self.getArgs().location)

        if self.getArgs().localBootParameters is not None:
            hp.setLocalBootParams(self.getArgs().localBootParameters)

        if self.getArgs().vcProfile is not None:
            spApi = SoftwareProfileWsApi(username=self.getUsername,
                                         password=self.getPassword(),
                                         baseurl=self.getUrl())
            sp = spApi.getSoftwareProfile(self.getArgs().vcProfile)

            hp.setHypervisorSoftwareProfileId(sp.getId())

        if self.getArgs().bClearHypervisorProfile:
            hp.setHypervisorSoftwareProfileId(None)

        if self.getArgs().maxUnits is not None:
            hp.setMaxUnits(self.getArgs().maxUnits)

        if self.getArgs().cost is not None:
            hp.setCost(self.getArgs().cost)

        if self.getArgs().resourceAdapter:
            resourceAdapter = ResourceAdapter(
                name=self.getArgs().resourceAdapter)
            hp.setResourceAdapter(resourceAdapter)

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
            nodeApi = getNodeApi(self.getUsername, self.getPassword())

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
                netArgs = netstring.split('/')
                if len(netArgs) != 3:
                    raise InvalidCliRequest(
                        _('Incorrect input format for --delete-network'
                          ' ("address/mask/device")'))

                dnet, dmask, ddev = netArgs

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
                    print(('Ignoring deletion of non-existent network:'
                           ' %s/%s/%s' % (dnet, dmask, ddev)))

            hp.setNetworks(out)

        if self.getArgs().addNetwork:
            networkApi = NetworkWsApi(username=self.getUsername,
                                      password=self.getPassword(),
                                      baseurl=self.getUrl())
            for netstring in self.getArgs().addNetwork:
                netArgs = netstring.split('/')
                if len(netArgs) != 3:
                    raise InvalidCliRequest(
                        _('Incorrect input format for --add-network'
                          ' ("address/mask/device")'))

                anet, amask, adev = netArgs
                networkApi.getNetwork(anet, amask)
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
