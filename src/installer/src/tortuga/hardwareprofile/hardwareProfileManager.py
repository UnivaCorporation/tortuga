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

# pylint: disable=no-name-in-module,no-member

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm.session import Session
from tortuga.config.configManager import ConfigManager
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.db.networkDbApi import NetworkDbApi
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.objects.networkDevice import NetworkDevice
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.utility import validation
from tortuga.utility.network import fixNetworkDeviceName


class HardwareProfileManager(TortugaObjectManager):
    def __init__(self):
        super(HardwareProfileManager, self).__init__()

        self._hpDbApi = HardwareProfileDbApi()
        self._spDbApi = SoftwareProfileDbApi()
        self._networkDbApi = NetworkDbApi()
        self._globalParameterDbApi = GlobalParameterDbApi()
        self._nodeDbApi = NodeDbApi()

    def getHardwareProfileList(self,
                               session: Session,
                               optionDict: Optional[Union[Dict[str, str], None]] = None,
                               tags: Optional[Union[Dict[str, str], None]] = None):
        """
        Return all of the hardwareprofiles with referenced components
        in this hardwareprofile
        """

        return self._hpDbApi.getHardwareProfileList(
            session, optionDict=optionDict, tags=tags)

    def setIdleSoftwareProfile(self, session: Session,
                               hardwareProfileName: str,
                               softwareProfileName: Optional[Union[str, None]] = None):
        """
        Set idle software profile
        """

        return self._hpDbApi.setIdleSoftwareProfile(
            session, hardwareProfileName, softwareProfileName)

    def getHardwareProfile(self, session: Session, name: str,
                           optionDict: Optional[Union[dict, None]] = None):
        return self._hpDbApi.getHardwareProfile(session, name, optionDict)

    def getHardwareProfileById(self, session: Session, id_, optionDict=None):
        return self._hpDbApi.getHardwareProfileById(session, id_, optionDict)

    def addAdmin(self, session: Session, hardwareProfileName: str,
                 adminUsername: str):
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """

        return self._hpDbApi.addAdmin(
            session, hardwareProfileName, adminUsername)

    def deleteAdmin(self, session: Session, hardwareProfileName: str,
                    adminUsername: str):
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                HardwareProfileNotFound
        """

        return self._hpDbApi.deleteAdmin(
            session, hardwareProfileName, adminUsername)

    def updateHardwareProfile(self, session: Session,
                              hardwareProfileObject: Any):
        """
        Update a hardware profile in the database that matches the passed
        in hardware profile object.  The ID is used as the primary matching
        criteria.

            Returns:
                None
            Throws:
                TortugaException
                HardwareProfileNotFound
                InvalidArgument

        """

        self.getLogger().debug(
            'Updating hardware profile [%s]' % (
                hardwareProfileObject.getName()))

        # First get the object from the db we are updating...
        existingProfile = self.getHardwareProfileById(
            session, hardwareProfileObject.getId())

        if hardwareProfileObject.getInstallType() and \
            hardwareProfileObject.getInstallType() != \
                existingProfile.getInstallType():
            raise InvalidArgument(
                'Hardware profile installation type cannot be'
                ' changed' % (hardwareProfileObject.getName()))

        self._hpDbApi.updateHardwareProfile(session, hardwareProfileObject)

    def createHardwareProfile(self, session: Session,
                              hwProfileSpec: HardwareProfile,
                              settingsDict: Optional[Union[dict, None]] = None):
        bUseDefaults = settingsDict['defaults'] \
            if settingsDict and 'defaults' in settingsDict else False

        osInfo = settingsDict['osInfo'] \
            if settingsDict and \
            settingsDict and 'osInfo' in settingsDict else None

        validation.validateProfileName(hwProfileSpec.getName())

        if hwProfileSpec.getDescription() is None:
            hwProfileSpec.setDescription(
                '%s Nodes' % (hwProfileSpec.getName()))

        installerNode = self._nodeDbApi.getNode(
            session,
            ConfigManager().getInstaller(),
            {'softwareprofile': True})

        if bUseDefaults:
            if not hwProfileSpec.getNetworks():
                # No <network>...</network> entries found in the template,
                # use the default provisioning interface from the primary
                # installer.

                # Find first provisioning network and use it
                for nic in installerNode.getNics():
                    network = nic.getNetwork()
                    if network.getType() == 'provision':
                        # for now set the default interface to be index 0
                        # with the same device
                        networkDevice = fixNetworkDeviceName(
                            nic.getNetworkDevice().getName())

                        network.setNetworkDevice(
                            NetworkDevice(name=networkDevice))

                        hwProfileSpec.getNetworks().append(network)

                        break
                else:
                    raise NetworkNotFound(
                        'Unable to find provisioning network')
            else:
                # Ensure network device is defined
                installerNic = None

                for network in hwProfileSpec.getNetworks():
                    for installerNic in installerNode.getNics():
                        installerNetwork = installerNic.getNetwork()

                        if network.getId() and \
                           network.getId() == installerNetwork.getId():
                            break
                        elif network.getAddress() and \
                            network.getAddress() == \
                            installerNetwork.getAddress() and \
                            network.getNetmask() and \
                            network.getNetmask() == \
                                installerNetwork.getNetmask():
                            break
                    else:
                        # Unable to find network matching specification in
                        # template.

                        raise NetworkNotFound(
                            'Unable to find provisioning network [%s]' % (
                                network))

                    networkDevice = fixNetworkDeviceName(
                        installerNic.getNetworkDevice().getName())

                    network.setNetworkDevice(
                        NetworkDevice(name=networkDevice))

        if hwProfileSpec.getIdleSoftwareProfile():
            # <idleSoftwareProfileId>...</idleSoftwareProfileId> is always
            # contained within the output of get-hardwareprofile.  If the
            # command-line option '--idleSoftwareProfile' is specified, it
            # overrides the
            # <idleSoftwareProfileId>...</idleSoftwareProfileId> element
            idleSoftwareProfile = self._spDbApi.getSoftwareProfile(
                session, hwProfileSpec.getIdleSoftwareProfile().getName())

            hwProfileSpec.setIdleSoftwareProfileId(
                idleSoftwareProfile.getId())

        if not osInfo:
            osInfo = installerNode.getSoftwareProfile().getOsInfo()

        osObjFactory = osUtility.getOsObjectFactory(osInfo.getName())

        if not hwProfileSpec.getKernel():
            hwProfileSpec.setKernel(
                osObjFactory.getOsSysManager().getKernel(osInfo))

        if not hwProfileSpec.getInitrd():
            hwProfileSpec.setInitrd(
                osObjFactory.getOsSysManager().getInitrd(osInfo))

        self._hpDbApi.addHardwareProfile(session, hwProfileSpec)

        # Iterate over all networks in the newly defined hardware profile
        # and build assocations to provisioning NICs
        if bUseDefaults:
            for network in \
                [network for network in hwProfileSpec.getNetworks()
                 if network.getType() == 'provision']:
                # Get provisioning nic for network
                try:
                    provisioningNic = self.getProvisioningNicForNetwork(
                        session, network.getAddress(), network.getNetmask())
                except NicNotFound:
                    # There is currently no provisioning NIC defined for
                    # this network.  This is not a fatal error.
                    continue

                self.setProvisioningNic(
                    session, hwProfileSpec.getName(), provisioningNic.getId())

    def deleteHardwareProfile(self, session: Session, name: str) -> None:
        """
        Delete hardwareprofile by name.
        """

        self._hpDbApi.deleteHardwareProfile(session, name)

        self.getLogger().info('Deleted hardware profile [%s]' % (name))

    def updateSoftwareOverrideAllowed(self, session: Session,
                                      hardwareProfileName: str,
                                      flag: bool) -> None:
        self._hpDbApi.updateSoftwareOverrideAllowed(
            session, hardwareProfileName, flag)

    def setProvisioningNic(self, session: Session, hardwareProfileName: str,
                           nicId: int):
        return self._hpDbApi.setProvisioningNic(
            session, hardwareProfileName, nicId)

    def getProvisioningNicForNetwork(self, session: Session, network: str,
                                     netmask: str):
        return self._hpDbApi.getProvisioningNicForNetwork(
            session, network, netmask)

    def copyHardwareProfile(self, session: Session, srcHardwareProfileName: str,
                            dstHardwareProfileName: str):
        validation.validateProfileName(dstHardwareProfileName)

        self.getLogger().info(
            'Copying hardware profile [%s] to [%s]' % (
                srcHardwareProfileName, dstHardwareProfileName))

        return self._hpDbApi.copyHardwareProfile(
            session, srcHardwareProfileName, dstHardwareProfileName)

    def getNodeList(self, session: Session, hardwareProfileName: str):
        return self._hpDbApi.getNodeList(session, hardwareProfileName)
