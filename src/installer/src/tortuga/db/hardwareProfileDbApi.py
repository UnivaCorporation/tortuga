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

from typing import Optional, Union

import sqlalchemy.exc
from sqlalchemy.orm.session import Session

import tortuga.objects.nic
from tortuga.config.configManager import ConfigManager
from tortuga.db.adminsDbHandler import AdminsDbHandler
from tortuga.db.dbManager import DbManager
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
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
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList

from .models.hardwareProfile import HardwareProfile as HardwareProfileModel
from .models.hardwareProfileNetwork import HardwareProfileNetwork
from .models.networkDevice import NetworkDevice


class HardwareProfileDbApi(TortugaDbApi):
    """
    HardwareProfile DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._hardwareProfilesDbHandler = HardwareProfilesDbHandler()
        self._nodesDbHandler = NodesDbHandler()
        self._globalParametersDbHandler = GlobalParametersDbHandler()
        self._adminsDbHandler = AdminsDbHandler()
        self._nicsDbHandler = NicsDbHandler()
        self._resourceAdaptersDbHandler = ResourceAdaptersDbHandler()
        self._networkDevicesDbHandler = NetworkDevicesDbHandler()
        self._networksDbHandler = NetworksDbHandler()

    def getHardwareProfile(self, name: str,
                           optionDict: Optional[Union[dict, None]] = None):
        """
        Get hardwareProfile from the db.

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbHardwareProfile = \
                self._hardwareProfilesDbHandler.getHardwareProfile(
                    session, name)

            self.loadRelations(dbHardwareProfile, optionDict)
            self.loadRelations(dbHardwareProfile, dict(tags=True))

            return HardwareProfile.getFromDbDict(
                dbHardwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getHardwareProfileById(self, hardwareProfileId: int,
                               optionDict: Optional[Union[dict, None]] = None):
        """
        Get hardwareProfile from the db.

            Returns:
                hardwareProfile
            Throws:
                HardwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfileById(session, hardwareProfileId)

            self.loadRelations(dbHardwareProfile, optionDict)

            return HardwareProfile.getFromDbDict(
                dbHardwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getHardwareProfileList(self, optionDict: Optional[Union[dict, None]] = None,
                               tags: Optional[Union[dict, None]] = None):
        """
        Get list of all available hardwareProfiles from the db.

            Returns:
                [hardwareProfile]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbHardwareProfileList = self._hardwareProfilesDbHandler.\
                getHardwareProfileList(session, tags=tags)

            hardwareProfileList = TortugaObjectList()

            for dbHardwareProfile in dbHardwareProfileList:
                # For now expand networks
                self.loadRelation(
                    dbHardwareProfile, 'hardwareprofilenetworks')

                self.loadRelations(dbHardwareProfile, optionDict)

                self.loadRelations(dbHardwareProfile, dict(tags=True))

                hardwareProfileList.append(
                    HardwareProfile.getFromDbDict(
                        dbHardwareProfile.__dict__))

            return hardwareProfileList
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def setIdleSoftwareProfile(self, hardwareProfileName,
                               softwareProfileName=None):
        """
        Sets the idle software profile

        Returns:
            -none-

        Raises:
            SoftwareProfileNotFound
            SoftwareProfileNotIdle
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = SoftwareProfilesDbHandler().\
                getSoftwareProfile(session, softwareProfileName) \
                if softwareProfileName else None

            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            self._hardwareProfilesDbHandler.setIdleSoftwareProfile(
                dbHardwareProfile, dbSoftwareProfile)

            session.commit()
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def addHardwareProfile(self, hardwareProfile, session=None):
        """
        Insert hardwareProfile into the db.

            Returns:
                (none)
            Throws:
                HardwareProfileAlreadyExists
                DbError
        """

        # Keep local 'session' instance.  If 'session' is None,
        # ensure transaction is committed before returning to the
        # caller, otherwise the caller is responsible.  On exceptions,
        # the rollback is performed regardless.

        _session = session

        if _session is None:
            _session = DbManager().openSession()

        try:
            try:
                self._hardwareProfilesDbHandler.getHardwareProfile(
                    _session, hardwareProfile.getName())

                raise HardwareProfileAlreadyExists(
                    'Hardware profile [%s] already exists' % (
                        hardwareProfile))
            except HardwareProfileNotFound as ex:
                pass

            dbHardwareProfile = self.__populateHardwareProfile(
                _session, hardwareProfile)

            _session.add(dbHardwareProfile)

            if session is None:
                _session.commit()

            self.getLogger().info(
                'Added hardware profile [%s]' % (dbHardwareProfile.name))
        except TortugaException:
            _session.rollback()
            raise
        except Exception as ex:
            _session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            if session is None:
                DbManager().closeSession()

    def deleteHardwareProfile(self, name):
        """
        Delete hardwareProfile from the db.

            Returns:
                None
            Throws:
                HardwareProfileNotFound
                DbError
                TortugaException
        """

        session = DbManager().openSession()

        try:
            hwProfile = self._hardwareProfilesDbHandler.getHardwareProfile(
                session, name)

            if hwProfile.nodes:
                raise TortugaException(
                    'Unable to remove hardware profile with associated'
                    ' nodes')

            # First delete the mappings
            hwProfile.mappedsoftwareprofiles = []

            self.getLogger().debug(
                'Marking hardware profile [%s] for deletion' % (name))

            session.delete(hwProfile)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def copyHardwareProfile(self, srcHardwareProfileName,
                            dstHardwareProfileName):
        session = DbManager().openSession()

        try:
            srcHardwareProfile = self.getHardwareProfile(
                srcHardwareProfileName, {
                    'admins': True,
                    'hardwareprofilenetworks': True,
                    'nics': True,
                    'resourceadapter': True,
                })

            dstHardwareProfile = \
                self.getHardwareProfile(srcHardwareProfileName)

            dstHardwareProfile.setName(dstHardwareProfileName)

            newDescription = 'Copy of %s' % (
                dstHardwareProfile.getDescription())

            dstHardwareProfile.setDescription(newDescription)

            dstHardwareProfile.setNetworks(srcHardwareProfile.getNetworks())

            dstHardwareProfile.setProvisioningNics(
                srcHardwareProfile.getProvisioningNics())

            dstHardwareProfile.setResourceAdapter(
                srcHardwareProfile.getResourceAdapter())

            self.addHardwareProfile(dstHardwareProfile, session)

            session.commit()
        finally:
            DbManager().closeSession()

    def addAdmin(self, hardwareProfileName, adminUsername):
        """
        Add an admin to this hardware profile

        Raises:
            AdminAlreadyExists
        """

        session = DbManager().openSession()

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
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def deleteAdmin(self, hardwareProfileName, adminUsername):
        """
        Delete an admin from a hardware profile

        Raises:
            AdminNotFound
        """

        session = DbManager().openSession()

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
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def updateHardwareProfile(self, hardwareProfileObject):
        """ Update Hardware Profile Object """

        session = DbManager().openSession()

        try:
            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfileById(session,
                                       hardwareProfileObject.getId())

            self.__populateHardwareProfile(
                session, hardwareProfileObject, dbHardwareProfile)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def __getInstallerNode(self, session):
        return self._nodesDbHandler.getNode(
            session, ConfigManager().getInstaller())

    def __get_provisioning_nics(self, session):
        return self.__getInstallerNode(session).nics

    def __get_all_networks(self, session):
        return self._networksDbHandler.getNetworkList(session)

    def __get_network_devices(self, session): \
            # pylint: disable=no-self-use
        return session.query(NetworkDevice).all()

    def __populateHardwareProfile(self, session: Session,
                                  hardwareProfile: HardwareProfileModel,
                                  dbHardwareProfile: Optional[Union[HardwareProfileModel, None]] = None) -> HardwareProfileModel:
        """
        Helper function for creating / updating hardware profiles. If
        'dbHardwareProfile' is specified, this is an update (vs. add)
        operation

        Raises:
            NicNotFound
            ResourceAdapterNotFound
        """

        # Preload provisioning nics and networks
        prov_nics = self.__get_provisioning_nics(session)
        all_networks = self.__get_all_networks(session)

        networkdevices = self.__get_network_devices(session)

        # Validate hw profile
        if hardwareProfile.getName() is None:
            raise ConfigurationError('Hardware profile requires name.')

        if hardwareProfile.getNameFormat() is None:
            raise ConfigurationError(
                'Hardware profile requires name format field.')

        # Handle the special case of a hardware profile not having an
        # associated idle software profile (ie. Installer hardware
        # profile)
        idleSoftwareProfileId = hardwareProfile.getIdleSoftwareProfileId() \
            if hardwareProfile.getIdleSoftwareProfileId else None

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
            dbHardwareProfile.kernelParams = hardwareProfile.\
                getKernelParams()
            dbHardwareProfile.initrd = hardwareProfile.getInitrd()
            dbHardwareProfile.localBootParams = hardwareProfile.\
                getLocalBootParams()

        dbHardwareProfile.softwareOverrideAllowed = hardwareProfile.\
            getSoftwareOverrideAllowed()
        dbHardwareProfile.idleSoftwareProfileId = idleSoftwareProfileId
        dbHardwareProfile.location = hardwareProfile.getLocation()

        dbHardwareProfile.hypervisorSoftwareProfileId = hardwareProfile.\
            getHypervisorSoftwareProfileId()
        dbHardwareProfile.cost = hardwareProfile.getCost()

        # Add resource adapter
        resource_adapter_name = \
            hardwareProfile.getResourceAdapter().getName() \
            if hardwareProfile.getResourceAdapter() else 'default'

        dbHardwareProfile.resourceadapter = \
            self._resourceAdaptersDbHandler.getResourceAdapter(
                session, resource_adapter_name)

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

            # Lookup network device
            for network_device in networkdevices:
                if network.getNetworkDevice().getName() == network_device.name:
                    dbNetworkDevice = network_device

                    break
            else:
                dbNetworkDevice = NetworkDevice()
                dbNetworkDevice.name = network.getNetworkDevice().getName()

            # Now check if we have this one already...
            for dbHardwareProfileNetwork in \
                    dbHardwareProfile.hardwareprofilenetworks:
                if dbHardwareProfileNetwork.networkDeviceId == dbNetworkDevice.id and \
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
                    'Provisioning NIC with IP [%s] not found' % (nic.getIp()))

            if dbNic not in dbHardwareProfile.nics:
                dbHardwareProfile.nics.append(dbNic)

        return dbHardwareProfile

    def getHypervisorNodes(self, hardwareProfileName):
        """
        Get list of nodes that belong to hypervisorSoftwareProfileId
        assigned to the given hardware profile name.
        """

        session = DbManager().openSession()

        try:
            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            if not dbHardwareProfile.hypervisor:
                return TortugaObjectList()

            return self.getTortugaObjectList(
                Node, dbHardwareProfile.hypervisor.nodes)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def setProvisioningNic(self, hardwareProfileName, nicId):
        session = DbManager().openSession()

        try:
            dbNic = self._nicsDbHandler.getNicById(session, nicId)

            dbHardwareProfile = self._hardwareProfilesDbHandler.\
                getHardwareProfile(session, hardwareProfileName)

            dbHardwareProfile.nics.append(dbNic)

            session.commit()
        except sqlalchemy.exc.IntegrityError as ex:
            # Entry for this hwProfile/nicId already exists, ignore
            self.getLogger().debug(
                'setProvisioningNic(): entry already exists for'
                ' hwProfile=%s, nicId=%d' % (hardwareProfileName, nicId))
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getProvisioningNicForNetwork(self, network, netmask):
        """
        Raises:
            NicNotFound
        """

        session = DbManager().openSession()

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
        except TortugaException as exc:
            self.getLogger().exception('%s' % exc)
            raise
        finally:
            DbManager().closeSession()
