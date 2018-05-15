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

# pylint: disable=not-callable,multiple-statements,no-member

from typing import Optional, Dict

from sqlalchemy import func

from tortuga.db.adminsDbHandler import AdminsDbHandler
from tortuga.db.componentsDbHandler import ComponentsDbHandler
from tortuga.db.dbManager import DbManager
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.operatingSystemsDbHandler import OperatingSystemsDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.adminAlreadyExists import AdminAlreadyExists
from tortuga.exceptions.adminNotFound import AdminNotFound
from tortuga.exceptions.invalidPartitionScheme import InvalidPartitionScheme
from tortuga.exceptions.softwareProfileAlreadyExists import \
    SoftwareProfileAlreadyExists
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.updateSoftwareProfileFailed import \
    UpdateSoftwareProfileFailed
from tortuga.objects.component import Component
from tortuga.objects.node import Node
from tortuga.objects.partition import Partition
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.objects.tortugaObject import TortugaObjectList

from .models.partition import Partition as PartitionModel
from .models.softwareProfile import SoftwareProfile as SoftwareProfileModel


class SoftwareProfileDbApi(TortugaDbApi):
    """
    SoftwareProfile DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()
        self._globalParametersDbHandler = GlobalParametersDbHandler()
        self._adminsDbHandler = AdminsDbHandler()
        self._osDbHandler = OperatingSystemsDbHandler()

    def getSoftwareProfile(
            self, name: str,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Get softwareProfile from the db.

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, name)

            self.loadRelations(dbSoftwareProfile, optionDict)

            self.loadRelations(dbSoftwareProfile, dict(tags=True))

            return SoftwareProfile.getFromDbDict(
                dbSoftwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getSoftwareProfileById(
            self, softwareProfileId: int,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Get softwareProfile from the db.

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfileById(session, softwareProfileId)

            self.loadRelations(dbSoftwareProfile, optionDict)

            return SoftwareProfile.getFromDbDict(
                dbSoftwareProfile.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getSoftwareProfileList(self, tags=None):
        """
        Get list of all available softwareProfiles from the db.

            Returns:
                [softwareProfile]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfileList = self._softwareProfilesDbHandler.\
                getSoftwareProfileList(session, tags=tags)

            softwareProfileList = TortugaObjectList()

            for dbSoftwareProfile in dbSoftwareProfileList:
                self.loadRelations(dbSoftwareProfile, {
                    'components': True,
                    'partitions': True,
                    'hardwareprofiles': True,
                    'tags': True,
                })

                softwareProfileList.append(
                    SoftwareProfile.getFromDbDict(
                        dbSoftwareProfile.__dict__))

            return softwareProfileList
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getIdleSoftwareProfileList(self):
        """
        Get list of all available idle softwareProfiles from the db.

            Returns:
                [idle softwareProfile]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfileList = self._softwareProfilesDbHandler.\
                getIdleSoftwareProfileList(session)

            return self.getTortugaObjectList(
                SoftwareProfile, dbSoftwareProfileList)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def setIdleState(self, softwareProfileName, state):
        """
        Set idle state of a software profile

            Returns:
                -none-
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfileName)

            self.getLogger().debug(
                'Setting idle state [%s] on software profile [%s]' % (
                    state, dbSoftwareProfile.name))

            dbSoftwareProfile.isIdle = state

            session.commit()
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def addSoftwareProfile(self, softwareProfile, session=None):
        """
        Insert software profile into the db.

        Raises:
            SoftwareProfileAlreadyExists
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
                dbSoftwareProfile = self._softwareProfilesDbHandler.\
                    getSoftwareProfile(
                        _session, softwareProfile.getName())

                raise SoftwareProfileAlreadyExists(
                    'Software profile [%s] already exists' % (
                        softwareProfile))
            except SoftwareProfileNotFound as ex:
                pass

            dbSoftwareProfile = self.__populateSoftwareProfile(
                _session, softwareProfile)

            _session.query(func.max(SoftwareProfileModel.id)).one()

            softwareProfile.setId(dbSoftwareProfile.id)

            if session is None:
                _session.commit()

            self.getLogger().info(
                'Added software profile [%s]' % (dbSoftwareProfile.name))

            return dbSoftwareProfile
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

    def deleteSoftwareProfile(self, name):
        """
        Delete softwareProfile from the db.

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            # This role of this lookup is twofold.  One, it validates
            # the existence of the software profile to be deleted and
            # second, gets the id for looking up any associated nodes
            dbSwProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, name)

            if dbSwProfile.nodes:
                # The software profile cannot be removed while
                # associated
                # nodes exist
                raise TortugaException(
                    'Unable to delete software profile with'
                    ' associated nodes')

            if dbSwProfile.isIdle:
                # Ensure this software profile is not associated with
                # a hardware profile

                if dbSwProfile.hwprofileswithidle:
                    # This software profile is associated with one
                    # or more hardware profiles
                    raise TortugaException(
                        'Unable to delete software profile.'
                        '  This software profile is associated'
                        ' with one or more hardware profiles: [%s]'
                        % (' '.join(
                            [hwprofile.name
                             for hwprofile in dbSwProfile.
                             hwprofileswithidle])))

            # Proceed with software profile deletion
            self.getLogger().debug(
                'Marking software profile [%s] for deletion' % (name))

            session.delete(dbSwProfile)

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

    def getAllEnabledComponentList(self):
        """
        Get a list of all enabled components in the system

            Returns:
                [ components ]
            Throws:
                DbError
        """

        self.getLogger().debug('Retrieving enabled component list')

        with DbManager().session() as session:
            try:
                dbComponents = \
                    ComponentsDbHandler().getEnabledComponentList(session)

                return self.getTortugaObjectList(Component, dbComponents)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getEnabledComponentList(self, name):
        """
        Get a list of enabled components from the db.

            Returns:
                node
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            componentList = TortugaObjectList()

            for c in self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, name).components:
                self.loadRelation(c, 'kit')

                componentList.append(Component.getFromDbDict(c.__dict__))

            return componentList
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNodeList(self, softwareProfile):
        """
        Get list of nodes in 'softwareProfile'

            Returns:
                [node]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfile)

            nodeList = TortugaObjectList()

            for dbNode in dbSoftwareProfile.nodes:
                self.loadRelation(dbNode, 'hardwareprofile')

                nodeList.append(Node.getFromDbDict(dbNode.__dict__))

            return nodeList
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNodeListByNodeStateAndSoftwareProfileName(self, nodeState,
                                                     softwareProfileName):
        """
        Return a list of Node objects based on the specified node state
        and software profile
        """

        session = DbManager().openSession()

        try:
            dbNodes = self._nodesDbHandler.\
                getNodeListByNodeStateAndSoftwareProfileName(
                    session, nodeState, softwareProfileName)

            return self.getTortugaObjectList(Node, dbNodes)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getPartitionList(self, softwareProfileName):
        """
        Get a list of software profile partitions from the db.

            Returns:
                [partition]
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfileName)
            return self.getTortugaObjectList(
                Partition, dbSoftwareProfile.partitions)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def addPartition(self, partitionName, softwareProfileName):
        """
        Add software profile partition.

            Returns:
                partitionId
            Throws:
                PartitionAlreadyExists
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            self._softwareProfilesDbHandler.\
                addPartitionToSoftwareProfile(
                    session, partitionName, softwareProfileName)

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

    def deletePartition(self, partitionName, softwareProfileName):
        """
        Delete node from the db.

            Returns:
                None
            Throws:
                PartitionNotFound
                SoftwareProfileNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            self._softwareProfilesDbHandler.\
                deletePartitionFromSoftwareProfile(
                    session, partitionName, softwareProfileName)
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

    def addUsableHardwareProfileToSoftwareProfile(
            self, hardwareProfileName, softwareProfileName):
        """
         Add hardwareProfile to softwareProfile

            Returns:
                SoftwareUsesHardwareId
            Throws:
                HardwareProfileNotFound
                SoftwareProfileNotFound
                SoftwareUsesHardwareAlreadyExists
                DbError
        """

        session = DbManager().openSession()

        try:
            swUsesHwId = self._softwareProfilesDbHandler.\
                addUsableHardwareProfileToSoftwareProfile(
                    session, hardwareProfileName, softwareProfileName)
            session.commit()
            return swUsesHwId
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def deleteUsableHardwareProfileFromSoftwareProfile(
            self, hardwareProfileName, softwareProfileName):
        """
        Delete hardwareProfile from softwareProfile

            Returns:
                None
            Throws:
                HardwareProfileNotFound
                SoftwareProfileNotFound
                SoftwareUsesHardwareNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            self._softwareProfilesDbHandler.\
                deleteUsableHardwareProfileFromSoftwareProfile(
                    session, hardwareProfileName, softwareProfileName)

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

    def addAdmin(self, softwareProfileName, adminUsername):
        """ Add an admin to this software profile """
        session = DbManager().openSession()

        try:
            dbAdmin = self._adminsDbHandler.getAdmin(
                session, adminUsername)

            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfileName)

            if dbAdmin not in dbSoftwareProfile.admins:
                dbSoftwareProfile.admins.append(dbAdmin)
            else:
                raise AdminAlreadyExists(
                    'Admin [%s] already associated with %s' % (
                        adminUsername, softwareProfileName))
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

    def deleteAdmin(self, softwareProfileName, adminUsername):
        """ Delete an admin from a software profile """

        session = DbManager().openSession()
        try:
            dbAdmin = self._adminsDbHandler.getAdmin(
                session, adminUsername)

            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfileName)

            if dbAdmin in dbSoftwareProfile.admins:
                dbSoftwareProfile.admins.remove(dbAdmin)
            else:
                raise AdminNotFound(
                    'Admin [%s] not associated with software profile'
                    ' [%s]' % (adminUsername, softwareProfileName))

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

    def updateSoftwareProfile(self, softwareProfileObject):
        """ Update a software profile """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfileById(
                    session, softwareProfileObject.getId())
            self.__populateSoftwareProfile(
                session, softwareProfileObject, dbSoftwareProfile)
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

    def __populateSoftwareProfile(self, session, softwareProfile,
                                  dbSoftwareProfile=None):
        """
        Helper function for creating/updating dbSoftwareProfile Object
        """

        # Validate object
        if softwareProfile.getName() is None:
            raise UpdateSoftwareProfileFailed(
                'Software profile name required')

        if softwareProfile.getType() is None:
            raise UpdateSoftwareProfileFailed(
                'Software profile must have valid type')

        osInfo = softwareProfile.getOsInfo()
        if osInfo is None or osInfo.getName() is None:
            raise UpdateSoftwareProfileFailed(
                'Software profile must have valid operating system')

        if dbSoftwareProfile is None:
            dbSoftwareProfile = SoftwareProfileModel()

        dbOs = self._osDbHandler.addOsIfNotFound(session, osInfo)

        dbSoftwareProfile.name = softwareProfile.getName()
        dbSoftwareProfile.description = softwareProfile.getDescription()
        dbSoftwareProfile.kernel = softwareProfile.getKernel()
        dbSoftwareProfile.kernelParams = softwareProfile.getKernelParams()
        dbSoftwareProfile.initrd = softwareProfile.getInitrd()
        dbSoftwareProfile.os = dbOs
        dbSoftwareProfile.type = softwareProfile.getType()
        dbSoftwareProfile.minNodes = softwareProfile.getMinNodes()
        dbSoftwareProfile.isIdle = softwareProfile.getIsIdle()

        # Add partitions
        partitions = {}
        for partition in softwareProfile.getPartitions():
            # This is a new partition
            dbPartition = PartitionModel()

            dbPartition.name = partition.getName()
            dbPartition.device = partition.getDevice()
            dbPartition.mountPoint = partition.getMountPoint()
            dbPartition.fsType = partition.getFsType()
            dbPartition.size = partition.getSize()
            dbPartition.options = partition.getOptions()
            dbPartition.preserve = partition.getPreserve()
            dbPartition.bootLoader = partition.getBootLoader()
            dbPartition.diskSize = partition.getDiskSize()
            dbPartition.directAttachment = partition.getDirectAttachment()
            dbPartition.indirectAttachment = partition.\
                getIndirectAttachment()
            dbPartition.sanVolume = partition.getSanVolume()

            if not dbPartition.name:
                raise InvalidPartitionScheme(
                    'Invalid partition in software profile:'
                    ' missing or empty name')

            if not dbPartition.device:
                raise InvalidPartitionScheme(
                    'Invalid partition in software profile:'
                    ' missing or empty device')

            if not dbPartition.fsType:
                raise InvalidPartitionScheme(
                    'Invalid partition [%s/%s] in software profile:'
                    ' missing or empty fsType' % (
                        dbPartition.name, dbPartition.device))

            if dbPartition.size is None:
                raise InvalidPartitionScheme(
                    'Invalid partition [%s/%s] in software profile:'
                    ' missing size' % (
                        dbPartition.name, dbPartition.device))

            if partitions.get(
                    (dbPartition.name, dbPartition.device)) is not None:
                # Duplicate partition ...error
                raise UpdateSoftwareProfileFailed(
                    'Duplicate partition [%s/%s] found' % (
                        dbPartition.name, dbPartition.device))

            try:
                int(dbPartition.size)
            except ValueError:
                raise InvalidPartitionScheme(
                    'Invalid partition [%s/%s] in software profile:'
                    ' non-integer size' % (
                        dbPartition.name, dbPartition.device))

            try:
                if dbPartition.diskSize is not None:
                    int(dbPartition.diskSize)
            except ValueError:
                raise InvalidPartitionScheme(
                    'Invalid partition [%s/%s] in software profile:'
                    ' non-integer disk size' % (
                        dbPartition.name, dbPartition.device))

            bGrow = partition.getGrow()
            if bGrow is not None:
                dbPartition.grow = bGrow

            maxSize = partition.getMaxSize()
            if maxSize is not None:
                dbPartition.maxSize = maxSize

            partitions[(dbPartition.name, dbPartition.device)] = \
                dbPartition

        # Delete out the old ones
        dbSoftwareProfile.partitions = []

        session.flush()

        dbSoftwareProfile.partitions = list(partitions.values())

        session.add(dbSoftwareProfile)

        session.flush()

        return dbSoftwareProfile

    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        session = DbManager().openSession()

        srcSoftwareProfile = self.getSoftwareProfile(
            srcSoftwareProfileName, {
                'partitions': True,
                'components': True,
            })

        dstSoftwareProfile = self.getSoftwareProfile(
            srcSoftwareProfileName)
        dstSoftwareProfile.setName(dstSoftwareProfileName)
        newDescription = 'Copy of %s' % (
            dstSoftwareProfile.getDescription())
        dstSoftwareProfile.setDescription(newDescription)

        # partitions
        dstSoftwareProfile.setPartitions(
            srcSoftwareProfile.getPartitions())

        # Finally add the software profile
        dstSoftwareProfile = self.addSoftwareProfile(
            dstSoftwareProfile, session)

        # Enable components separately
        srcCompList = self.getEnabledComponentList(srcSoftwareProfileName)

        for srcComp in srcCompList:
            if srcComp.getKit().getIsOs() or srcComp.getName() == 'core':
                self._softwareProfilesDbHandler.\
                    addComponentToSoftwareProfileEx(
                        session, srcComp.getId(), dstSoftwareProfile)

        session.commit()

    def getUsableNodes(self, name):
        """
        Return list of nodes with same software/hardware profile mapping
        as the specified software profile.
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, name)

            nodes = [
                dbNode for dbHardwareProfile in
                dbSoftwareProfile.hardwareprofiles
                for dbNode in dbHardwareProfile.nodes]

            return self.getTortugaObjectList(Node, nodes)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()
