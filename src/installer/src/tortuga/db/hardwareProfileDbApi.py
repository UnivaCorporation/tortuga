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

from typing import Dict, List, Optional

import sqlalchemy.exc
import tortuga.objects.nic
from sqlalchemy.orm.session import Session
from tortuga.config.configManager import ConfigManager
from tortuga.db.adminsDbHandler import AdminsDbHandler
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.models.hardwareProfileTag import HardwareProfileTag
from tortuga.db.models.network import Network
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.networkDevicesDbHandler import NetworkDevicesDbHandler
from tortuga.db.networksDbHandler import NetworksDbHandler
from tortuga.db.nicsDbHandler import NicsDbHandler
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.resourceAdaptersDbHandler import ResourceAdaptersDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.adminAlreadyExists import AdminAlreadyExists
from tortuga.exceptions.adminNotFound import AdminNotFound
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.hardwareProfileAlreadyExists import \
    HardwareProfileAlreadyExists
from tortuga.exceptions.hardwareProfileNotFound import HardwareProfileNotFound
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.objects.tortugaObject import TortugaObjectList

from .models.hardwareProfile import HardwareProfile as HardwareProfileModel
from .models.hardwareProfileNetwork import HardwareProfileNetwork
from .tagsDbApiMixin import TagsDbApiMixin


OptionDict = Dict[str, bool]
Tags = Dict[str, Optional[str]]


class HardwareProfileDbApi(TagsDbApiMixin, TortugaDbApi):
    """
    HardwareProfile DB API class.

    """
    tag_model = HardwareProfileTag

    def __init__(self):
        super().__init__()

        self._hardwareProfilesDbHandler = HardwareProfilesDbHandler()
        self._nodesDbHandler = NodesDbHandler()
        self._globalParametersDbHandler = GlobalParametersDbHandler()
        self._adminsDbHandler = AdminsDbHandler()
        self._nicsDbHandler = NicsDbHandler()
        self._resourceAdaptersDbHandler = ResourceAdaptersDbHandler()
        self._networkDevicesDbHandler = NetworkDevicesDbHandler()
        self._networksDbHandler = NetworksDbHandler()

    def getHardwareProfile(self, session: Session, name: str,
                           optionDict: Optional[OptionDict] = None) \
            -> HardwareProfile:
        """
        Get hardwareProfile from the db.

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                DbError
        """

        try:
            dbHardwareProfile = \
                self._hardwareProfilesDbHandler.getHardwareProfile(
                    session, name)

            self.loadRelations(
                dbHardwareProfile, get_default_relations(optionDict))

            return HardwareProfile.getFromDbDict(
                dbHardwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def getHardwareProfileById(
            self, session: Session, hardwareProfileId: int,
            optionDict: Optional[OptionDict] = None) -> HardwareProfile:
        """
        Get hardwareProfile from the db.

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                DbError
        """

        try:
            dbHardwareProfile = \
                self._hardwareProfilesDbHandler.getHardwareProfileById(
                    session, hardwareProfileId)

            self.loadRelations(
                dbHardwareProfile, get_default_relations(optionDict))

            return HardwareProfile.getFromDbDict(dbHardwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def getHardwareProfileList(
            self, session: Session, optionDict: Optional[OptionDict] = None,
            tags: Optional[Tags] = None) -> TortugaObjectList:
        """
        Get list of all available hardwareProfiles from the db.

            Returns:
                [hardwareProfile]
            Throws:
                DbError
        """

        try:
            dbHardwareProfileList = \
                self._hardwareProfilesDbHandler.getHardwareProfileList(
                    session, tags=tags)

            hardwareProfileList = TortugaObjectList()

            for dbHardwareProfile in dbHardwareProfileList:
                options = dict.copy(optionDict or {})
                options['hardwareprofilenetworks'] = True

                self.loadRelations(
                    dbHardwareProfile, get_default_relations(options))

                hardwareProfileList.append(
                    HardwareProfile.getFromDbDict(
                        dbHardwareProfile.__dict__))

            return hardwareProfileList
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def addHardwareProfile(
            self, session: Session,
            hardwareProfile: HardwareProfile) -> None:
        """
        Insert hardwareProfile into the db.

            Returns:
                (none)
            Throws:
                HardwareProfileAlreadyExists
                DbError
        """

        try:
            try:
                self._hardwareProfilesDbHandler.getHardwareProfile(
                    session, hardwareProfile.getName())

                raise HardwareProfileAlreadyExists(
                    'Hardware profile [%s] already exists' % (
                        hardwareProfile))
            except HardwareProfileNotFound as ex:
                pass

            dbHardwareProfile = self.__populateHardwareProfile(
                session, hardwareProfile)

            session.add(dbHardwareProfile)
            session.flush()
            self._set_tags(dbHardwareProfile, hardwareProfile.getTags())
            session.commit()

            self._logger.info(
                'Added hardware profile [%s]' % (dbHardwareProfile.name))
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def deleteHardwareProfile(self, session: Session, name: str) -> None:
        """
        Delete hardwareProfile from the db.

            Returns:
                None
            Throws:
                HardwareProfileNotFound
                DbError
                TortugaException
        """

        try:
            hwProfile = self._hardwareProfilesDbHandler.getHardwareProfile(
                session, name)

            if hwProfile.nodes:
                raise TortugaException(
                    'Unable to delete hardware profile with associated nodes'
                )

            # First delete the mappings
            hwProfile.mappedsoftwareprofiles = []

            self._logger.debug(
                'Marking hardware profile [%s] for deletion' % (name))

            session.delete(hwProfile)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def copyHardwareProfile(self, session: Session,
                            srcHardwareProfileName: str,
                            dstHardwareProfileName: str):
        srcHardwareProfile = self.getHardwareProfile(
            session,
            srcHardwareProfileName, {
                'admins': True,
                'hardwareprofilenetworks': True,
                'nics': True,
                'resourceadapter': True,
            })

        dstHardwareProfile = \
            self.getHardwareProfile(session, srcHardwareProfileName)

        dstHardwareProfile.setName(dstHardwareProfileName)

        newDescription = 'Copy of %s' % (
            dstHardwareProfile.getDescription())

        dstHardwareProfile.setDescription(newDescription)

        dstHardwareProfile.setNetworks(srcHardwareProfile.getNetworks())

        dstHardwareProfile.setProvisioningNics(
            srcHardwareProfile.getProvisioningNics())

        dstHardwareProfile.setResourceAdapter(
            srcHardwareProfile.getResourceAdapter())

        self.addHardwareProfile(session, dstHardwareProfile)

    def addAdmin(
            self, session: Session, hardwareProfileName,
            adminUsername: str) -> None:
        """
        Add an admin to this hardware profile

        Raises:
            AdminAlreadyExists
        """

        try:
            dbAdmin = self._adminsDbHandler.getAdmin(
                session, adminUsername)

            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            if dbAdmin in dbHardwareProfile.admins:
                raise AdminAlreadyExists(
                    'The admin %s is already associated with %s.' % (
                        adminUsername, hardwareProfileName))

            dbHardwareProfile.admins.append(dbAdmin)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def deleteAdmin(
            self, session: Session, hardwareProfileName: str,
            adminUsername: str) -> None:
        """
        Delete an admin from a hardware profile

        Raises:
            AdminNotFound
        """

        try:
            dbAdmin = self._adminsDbHandler.getAdmin(session, adminUsername)

            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            if dbAdmin not in dbHardwareProfile.admins:
                raise AdminNotFound(
                    'Admin user [%s] not associated with %s.' % (
                        adminUsername, hardwareProfileName))

            dbHardwareProfile.admins.remove(dbAdmin)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def updateHardwareProfile(
            self, session: Session,
            hardwareProfileObject: HardwareProfile) -> None:
        """
        Update Hardware Profile Object
        """

        try:
            dbHardwareProfile = \
                self._hardwareProfilesDbHandler.getHardwareProfileById(
                    session, hardwareProfileObject.getId())

            self.__populateHardwareProfile(
                session, hardwareProfileObject, dbHardwareProfile)
            self._set_tags(dbHardwareProfile, hardwareProfileObject.getTags())
            session.commit()

        except TortugaException:
            session.rollback()
            raise

        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def __getInstallerNode(self, session: Session) -> Node:
        return self._nodesDbHandler.getNode(
            session, ConfigManager().getInstaller())

    def __get_provisioning_nics(self, session: Session) -> List[Nic]:
        return self.__getInstallerNode(session).nics

    def __get_all_networks(self, session: Session) -> List[Network]:
        return self._networksDbHandler.getNetworkList(session)

    def __populateHardwareProfile(
            self, session: Session, hardwareProfile: HardwareProfile,
            dbHardwareProfile: Optional[HardwareProfileModel] = None) \
            -> HardwareProfileModel:
        """
        Helper function for creating / updating hardware profiles. If
        'dbHardwareProfile' is specified, this is an update (vs. add)
        operation

        Raises:
            NicNotFound
            ResourceAdapterNotFound
            InvalidArgument
            ConfigurationError

        """
        # Preload provisioning nics and networks
        prov_nics = self.__get_provisioning_nics(session)
        all_networks = self.__get_all_networks(session)

        # Validate hw profile
        if hardwareProfile.getName() is None:
            raise ConfigurationError('Hardware profile requires name.')

        if hardwareProfile.getNameFormat() is None:
            raise ConfigurationError(
                'Hardware profile requires name format field.')

        if dbHardwareProfile is None:
            dbHardwareProfile = HardwareProfileModel()

        dbHardwareProfile.name = hardwareProfile.getName()
        dbHardwareProfile.description = hardwareProfile.getDescription()
        dbHardwareProfile.nameFormat = hardwareProfile.getNameFormat()

        if hardwareProfile.getInstallType() is None:
            if hardwareProfile.getLocation() == 'remote':
                dbHardwareProfile.installType = 'bootstrap'
            else:
                dbHardwareProfile.installType = 'package'
        else:
            dbHardwareProfile.installType = hardwareProfile.\
                getInstallType()

        if hardwareProfile.getLocation() != 'remote':
            dbHardwareProfile.kernel = hardwareProfile.getKernel()
            dbHardwareProfile.kernelParams = \
                hardwareProfile.getKernelParams()
            dbHardwareProfile.initrd = hardwareProfile.getInitrd()
            dbHardwareProfile.localBootParams = \
                hardwareProfile.getLocalBootParams()

        dbHardwareProfile.softwareOverrideAllowed = hardwareProfile.\
            getSoftwareOverrideAllowed()

        dbHardwareProfile.location = hardwareProfile.getLocation()

        dbHardwareProfile.cost = hardwareProfile.getCost()

        # Add resource adapter
        resource_adapter_name = \
            hardwareProfile.getResourceAdapter().getName() \
            if hardwareProfile.getResourceAdapter() else 'default'

        dbHardwareProfile.resourceadapter = \
            self._resourceAdaptersDbHandler.getResourceAdapter(
                session, resource_adapter_name)

        if hardwareProfile.getDefaultResourceAdapterConfig():
            adapter_cfg = None

            self._logger.debug(
                'Setting default resource adapter config: {}'.format(
                    hardwareProfile.getDefaultResourceAdapterConfig())
            )

            for adapter_cfg in \
                    dbHardwareProfile.resourceadapter.resource_adapter_config:
                if adapter_cfg.name == \
                        hardwareProfile.getDefaultResourceAdapterConfig():
                    break
            else:
                raise InvalidArgument(
                    'Resource adapter configuration profile [{}] is'
                    ' invalid'.format(
                        hardwareProfile.getDefaultResourceAdapterConfig())
                )

            dbHardwareProfile.default_resource_adapter_config = adapter_cfg
        else:
            dbHardwareProfile.default_resource_adapter_config = None

        # Add networks
        networks = []
        for network in hardwareProfile.getNetworks():
            for prov_network in all_networks:
                if prov_network.address == network.getAddress():
                    dbNetwork = prov_network

                    break
            else:
                raise NetworkNotFound(
                    'Network [%s] does not exist' % (network.getAddress()))

            dbNetworkDevice = \
                self._networkDevicesDbHandler.createNetworkDeviceIfNotExists(
                    session, network.getNetworkDevice().getName())

            # Now check if we have this one already...
            for dbHardwareProfileNetwork in \
                    dbHardwareProfile.hardwareprofilenetworks:
                if dbHardwareProfileNetwork.networkDeviceId == \
                        dbNetworkDevice.id and \
                        dbHardwareProfileNetwork.networkId == dbNetwork.id:
                    break
            else:
                dbHardwareProfileNetwork = HardwareProfileNetwork()
                dbHardwareProfileNetwork.hardwareprofile = dbHardwareProfile

                if dbNetwork.id is not None:
                    dbHardwareProfileNetwork.networkId = dbNetwork.id
                else:
                    dbHardwareProfileNetwork.network = dbNetwork

                dbHardwareProfileNetwork.hardwareProfileId = \
                    dbHardwareProfile.id

                if dbNetworkDevice.id is not None:
                    dbHardwareProfileNetwork.networkDeviceId = \
                        dbNetworkDevice.id
                else:
                    dbHardwareProfileNetwork.networkdevice = dbNetworkDevice

                dbHardwareProfile.hardwareprofilenetworks.append(
                    dbHardwareProfileNetwork)

            networks.append(dbHardwareProfileNetwork)

        # Now remove all old networks
        for dbNetwork in dbHardwareProfile.hardwareprofilenetworks:
            for network in networks:
                if network.networkDeviceId == dbNetwork.networkDeviceId \
                        and network.networkId == dbNetwork.networkId:
                    # Its a keeper
                    break
            else:
                # No match...delete time
                session.delete(dbNetwork)

        # Add provisioning Nics
        if hardwareProfile.getProvisioningNics():
            # Only one provisioning nic is possible
            nic = hardwareProfile.getProvisioningNics()[0]

            for prov_nic in prov_nics:
                if nic.getIp() == prov_nic.ip:
                    dbNic = prov_nic

                    break
            else:
                raise NicNotFound(
                    'Provisioning NIC with IP [%s] not found' % nic.getIp())

            if dbNic not in dbHardwareProfile.nics:
                dbHardwareProfile.nics.append(dbNic)

        return dbHardwareProfile

    def setProvisioningNic(
            self, session: Session, hardwareProfileName: str,
            nicId: int) -> None:
        try:
            dbNic = self._nicsDbHandler.getNicById(session, nicId)

            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            dbHardwareProfile.nics.append(dbNic)

            session.commit()
        except sqlalchemy.exc.IntegrityError as ex:
            # Entry for this hwProfile/nicId already exists, ignore
            self._logger.debug(
                'setProvisioningNic(): entry already exists for'
                ' hwProfile=%s, nicId=%d' % (hardwareProfileName, nicId))
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def getProvisioningNicForNetwork(
            self, session: Session, network: str, netmask: str) -> Nic:
        """
        Raises:
            NicNotFound
        """

        try:
            installer_node = self.__getInstallerNode(session)

            nics = [
                dbNic for dbNic in installer_node.hardwareprofile.nics
                if dbNic.network.address == network and
                dbNic.network.netmask == netmask]

            if not nics:
                raise NicNotFound(
                    'Unable to find provisioning NIC for network [%s]'
                    ' netmask [%s]' % (network, netmask))

            return tortuga.objects.nic.Nic.getFromDbDict(nics[0].__dict__)
        except TortugaException as ex:
            self._logger.exception(str(ex))
            raise


def get_default_relations(relations: Optional[OptionDict]):
    """
    Ensure hardware and software profiles and tags are populated when
    serializing node records.
    """

    result = relations.copy() if relations else {}

    # ensure software and hardware profile relations are loaded
    result.update({
        'tags': True,
        'resourceadapter': True,
        'default_resource_adapter_config': True,
    })

    return result
