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

from typing import Dict, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm.session import Session

from tortuga.db.adminsDbHandler import AdminsDbHandler
from tortuga.db.componentsDbHandler import ComponentsDbHandler
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
from .models.softwareProfileTag import SoftwareProfileTag
from .tagsDbApiMixin import TagsDbApiMixin


class SoftwareProfileDbApi(TagsDbApiMixin, TortugaDbApi):
    """
    SoftwareProfile DB API class.

    """
    tag_model = SoftwareProfileTag

    def __init__(self):
        super().__init__()

        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()
        self._globalParametersDbHandler = GlobalParametersDbHandler()
        self._adminsDbHandler = AdminsDbHandler()
        self._osDbHandler = OperatingSystemsDbHandler()

    def getSoftwareProfile(
            self, session, name: str,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Get softwareProfile from the db.

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        try:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, name)

            return self.__get_software_profile_obj(
                dbSoftwareProfile, options=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def __get_software_profile_obj(
            self, software_profile: SoftwareProfileModel,
            options: Optional[dict] = None) -> SoftwareProfile:
        """
        Deserialize SQLAlchemy object to TortugaObject
        """
        self.loadRelations(software_profile, options)

        self.loadRelations(software_profile, dict(tags=True))

        # if 'components' is specified, ensure 'kit' relationship is
        # also serialized
        if options and 'components' in options and options['components']:
            for component in software_profile.components:
                self.loadRelation(component, 'kit')

        software_profile_obj = SoftwareProfile.getFromDbDict(
            software_profile.__dict__)

        return software_profile_obj

    def getSoftwareProfileById(
            self, session: Session, softwareProfileId: int,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Get softwareProfile from the db.

            Returns:
               softwareProfile
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        try:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfileById(
                    session, softwareProfileId)

            return self.__get_software_profile_obj(
                dbSoftwareProfile, options=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getSoftwareProfileList(self, session: Session, tags=None):
        """
        Get list of all available softwareProfiles from the db.

            Returns:
                [softwareProfile]
            Throws:
                DbError
        """

        try:
            dbSoftwareProfileList = \
                self._softwareProfilesDbHandler.getSoftwareProfileList(
                    session, tags=tags)

            softwareProfileList = TortugaObjectList()

            for dbSoftwareProfile in dbSoftwareProfileList:
                softwareProfileList.append(
                    self.__get_software_profile_obj(
                        dbSoftwareProfile, options={
                            'components': True,
                            'partitions': True,
                            'hardwareprofiles': True,
                            'tags': True,
                        }))

            return softwareProfileList
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getIdleSoftwareProfileList(self, session: Session):
        """
        Get list of all available idle softwareProfiles from the db.

            Returns:
                [idle softwareProfile]
            Throws:
                DbError
        """

        try:
            dbSoftwareProfileList = \
                self._softwareProfilesDbHandler.getIdleSoftwareProfileList(
                    session)

            result = TortugaObjectList()

            for software_profile in dbSoftwareProfileList:
                self.__get_software_profile_obj(software_profile)

            return result
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def setIdleState(
            self, session: Session, softwareProfileName: str,
            state: str) -> None:
        """
        Set idle state of a software profile

            Returns:
                -none-
            Throws:
                DbError
        """

        try:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, softwareProfileName)

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

    def addSoftwareProfile(
            self, session: Session,
            softwareProfile: SoftwareProfile) -> SoftwareProfileModel:
        """
        Insert software profile into the db.

        Raises:
            SoftwareProfileAlreadyExists
            DbError
        """

        try:
            try:
                dbSoftwareProfile = self._softwareProfilesDbHandler.\
                    getSoftwareProfile(
                        session, softwareProfile.getName())

                raise SoftwareProfileAlreadyExists(
                    'Software profile [%s] already exists' % (
                        softwareProfile))
            except SoftwareProfileNotFound as ex:
                pass

            dbSoftwareProfile = self.__populateSoftwareProfile(
                session, softwareProfile)

            session.query(func.max(SoftwareProfileModel.id)).one()

            softwareProfile.setId(dbSoftwareProfile.id)

            self.getLogger().info(
                'Added software profile [%s]' % (dbSoftwareProfile.name))

            return dbSoftwareProfile
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise

    def deleteSoftwareProfile(self, session: Session, name: str) -> None:
        """
        Delete softwareProfile from the db.

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                DbError
        """

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

    def getAllEnabledComponentList(
            self, session: Session) -> TortugaObjectList:
        """
        Get a list of all enabled components in the system

            Returns:
                [ components ]
            Throws:
                DbError
        """

        self.getLogger().debug('Retrieving enabled component list')

        try:
            dbComponents = \
                ComponentsDbHandler().getEnabledComponentList(session)

            return self.getTortugaObjectList(Component, dbComponents)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getEnabledComponentList(
            self, session: Session, name: str) -> TortugaObjectList:
        """
        Get a list of enabled components from the db.

            Returns:
                node
            Throws:
                DbError
        """

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

    def getNodeList(
            self, session: Session,
            softwareProfile: SoftwareProfile) -> TortugaObjectList:
        """
        Get list of nodes in 'softwareProfile'

            Returns:
                [node]
            Throws:
                DbError
        """

        try:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, softwareProfile)

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

    def getPartitionList(
            self, session: Session, softwareProfileName: str) \
            -> TortugaObjectList:
        """
        Get a list of software profile partitions from the db.

            Returns:
                [partition]
            Throws:
                SoftwareProfileNotFound
                DbError
        """

        try:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, softwareProfileName)

            return self.getTortugaObjectList(
                Partition, dbSoftwareProfile.partitions)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def addPartition(
            self, session: Session, partitionName: str,
            softwareProfileName: str) -> None:
        """
        Add software profile partition.

            Returns:
                partitionId
            Throws:
                PartitionAlreadyExists
                SoftwareProfileNotFound
        """

        try:
            self._softwareProfilesDbHandler.addPartitionToSoftwareProfile(
                session, partitionName, softwareProfileName)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise

    def deletePartition(self, session: Session, partitionName: str,
                        softwareProfileName: str) -> None:
        """
        Delete node from the db.

            Returns:
                None
            Throws:
                PartitionNotFound
                SoftwareProfileNotFound
                DbError
        """

        try:
            self._softwareProfilesDbHandler.deletePartitionFromSoftwareProfile(
                session, partitionName, softwareProfileName)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise

    def addUsableHardwareProfileToSoftwareProfile(
            self, session: Session, hardwareProfileName: str,
            softwareProfileName: str) -> None:
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

        try:
            self._softwareProfilesDbHandler.addUsableHardwareProfileToSoftwareProfile(
                session, hardwareProfileName, softwareProfileName)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise

    def deleteUsableHardwareProfileFromSoftwareProfile(
            self, session: Session, hardwareProfileName: str,
            softwareProfileName: str) -> None:
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

    def addAdmin(self, session: Session, softwareProfileName: str,
                 adminUsername: str) -> None:
        """
        Add an admin to this software profile

        Raises:
            AdminAlreadyExists
        """

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

    def deleteAdmin(self, session: Session, softwareProfileName: str,
                    adminUsername: str) -> None:
        """
        Delete an admin from a software profile
        """

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

    def updateSoftwareProfile(
            self, session: Session,
            softwareProfileObject: SoftwareProfile) -> None:
        """
        Update a software profile
        """

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

    def __populateSoftwareProfile(
            self, session: Session, softwareProfile: SoftwareProfile,
            dbSoftwareProfile: Optional[SoftwareProfileModel] = None) \
            -> SoftwareProfileModel:
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
        dbSoftwareProfile.maxNodes = softwareProfile.getMaxNodes()
        dbSoftwareProfile.lockedState = softwareProfile.getLockedState()
        dbSoftwareProfile.isIdle = softwareProfile.getIsIdle()
        dbSoftwareProfile.dataRoot = softwareProfile.getDataRoot()
        #self.getLogger().debug('dbSoftwareProfile.dataRoot=%s'%dbSoftwareProfile.dataRoot)

        # Add partitions
        partitions: Dict[Tuple[str, str], Partition] = {}
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
        self._set_tags(dbSoftwareProfile, softwareProfile.getTags())

        session.add(dbSoftwareProfile)
        session.flush()

        return dbSoftwareProfile

    def copySoftwareProfile(self, session: Session,
                            srcSoftwareProfileName: str,
                            dstSoftwareProfileName: str) -> None:
        src_swprofile = self._softwareProfilesDbHandler.getSoftwareProfile(
            session, srcSoftwareProfileName)

        dst_swprofile = SoftwareProfileModel(
            name=dstSoftwareProfileName,
            description='Copy of %s' % (src_swprofile.description),
            kernel=src_swprofile.kernel,
            kernelParams=src_swprofile.kernelParams,
            initrd=src_swprofile.initrd,
            type=src_swprofile.type,
            minNodes=src_swprofile.minNodes,
            maxNodes=src_swprofile.maxNodes,
            lockedState=src_swprofile.lockedState,
            isIdle=src_swprofile.isIdle,
            dataRoot=src_swprofile.dataRoot
        )

        # os
        dst_swprofile.os = src_swprofile.os

        # admins
        for admin in src_swprofile.admins:
            dst_swprofile.admins.append(admin)

        # partitions
        for partition in src_swprofile.partitions:
            dst_swprofile.partitions.append(partition)

        # components
        for component in src_swprofile.components:
            dst_swprofile.components.append(component)

        # tags
        for tag in src_swprofile.tags:
            dst_swprofile.tags.append(tag)

        # kitsources
        for kitsource in src_swprofile.kitsources:
            dst_swprofile.kitsources.append(kitsource)

        # hardwareprofiles
        for hwprofile in src_swprofile.hardwareprofiles:
            dst_swprofile.hardwareprofiles.append(hwprofile)

        # idle hardware profiles
        for hwprofileswithidle in src_swprofile.hwprofileswithidle:
            dst_swprofile.hwprofileswithidle.append(hwprofileswithidle)

        session.add(dst_swprofile)

        session.commit()

    def getUsableNodes(self, session: Session, name: str) \
            -> TortugaObjectList:
        """
        Return list of nodes with same software/hardware profile mapping
        as the specified software profile.
        """

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
