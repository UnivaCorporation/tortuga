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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, or_

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.package import Package
from tortuga.db.models.partition import Partition
from tortuga.exceptions.softwareProfileNotFound \
    import SoftwareProfileNotFound
from tortuga.exceptions.softwareProfileComponentAlreadyExists \
    import SoftwareProfileComponentAlreadyExists
from tortuga.exceptions.softwareProfileComponentNotFound \
    import SoftwareProfileComponentNotFound
from tortuga.exceptions.hardwareProfileNotFound \
    import HardwareProfileNotFound
from tortuga.exceptions.softwareUsesHardwareAlreadyExists \
    import SoftwareUsesHardwareAlreadyExists
from tortuga.exceptions.softwareUsesHardwareNotFound \
    import SoftwareUsesHardwareNotFound
from tortuga.exceptions.partitionAlreadyExists \
    import PartitionAlreadyExists
from tortuga.exceptions.partitionNotFound import PartitionNotFound
from tortuga.db.componentsDbHandler import ComponentsDbHandler
from tortuga.exceptions.packageAlreadyExists import PackageAlreadyExists
from tortuga.exceptions.packageNotFound import PackageNotFound


class SoftwareProfilesDbHandler(TortugaDbObjectHandler):
    """
    This class handles softwareProfiles table.
    """

    def __init__(self):
        TortugaDbObjectHandler.__init__(self)

        self._componentsDbHandler = ComponentsDbHandler()

    def getSoftwareProfile(self, session, name):
        """
        Return softwareProfile.
        """

        self.getLogger().debug('Retrieving software profile [%s]' % (name))

        try:
            return session.query(SoftwareProfile).filter(
                SoftwareProfile.name == name).one()
        except NoResultFound:
            raise SoftwareProfileNotFound(
                'Software profile [%s] not found' % (name))

    def getSoftwareProfileById(self, session, _id):
        """
        Return software profile

        Raises:
            SoftwareProfileNotFound
        """

        self.getLogger().debug(
            'Retrieving software profile ID [%s]' % (_id))

        dbSoftwareProfile = session.query(SoftwareProfile).get(_id)

        if not dbSoftwareProfile:
            raise SoftwareProfileNotFound(
                'Software profile ID [%s] not found.' % (_id))

        return dbSoftwareProfile

    def getSoftwareProfileList(self, session, tags=None):
        """
        Get list of softwareProfiles from the db.
        """

        self.getLogger().debug('Retrieving software profile list')

        searchspec = []

        if tags:
            # Build searchspec from specified tags
            for tag in tags:
                if len(tag) == 2:
                    searchspec.append(
                        and_(SoftwareProfile.tags.any(name=tag[0]),
                             SoftwareProfile.tags.any(value=tag[1])))
                else:
                    searchspec.append(SoftwareProfile.tags.any(name=tag[0]))

        return session.query(SoftwareProfile).filter(
            or_(*searchspec)).order_by(SoftwareProfile.name).all()

    def getIdleSoftwareProfileList(self, session):
        """
        Get list of idle softwareProfiles from the db.
        """

        self.getLogger().debug('Retrieving idle software profile list')

        return session.query(SoftwareProfile).filter(
            SoftwareProfile.isIdle == 1).all()

    def __getHardwareProfile(self, session, hardwareProfileName): \
            # pylint: disable=no-self-use
        try:
            return session.query(HardwareProfile).filter(
                HardwareProfile.name == hardwareProfileName).one()
        except NoResultFound:
            raise HardwareProfileNotFound(
                'Hardware profile [%s] not found' % (hardwareProfileName))

    def addUsableHardwareProfileToSoftwareProfile(self, session,
                                                  hardwareProfileName,
                                                  softwareProfileName):
        """
        Add usable hardwareProfile to softwareProfile.

        Raises:
            HardwareProfileNotFound
        """

        self.getLogger().debug(
            'Adding hardware profile [%s] to software profile [%s]' % (
                hardwareProfileName, softwareProfileName))

        dbHardwareProfile = self.__getHardwareProfile(
            session, hardwareProfileName)

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        if dbHardwareProfile in dbSoftwareProfile.hardwareprofiles:
            raise SoftwareUsesHardwareAlreadyExists(
                'Software profile [%s] already mapped to hardware'
                ' profile [%s]' % (softwareProfileName, hardwareProfileName))

        dbSoftwareProfile.hardwareprofiles.append(dbHardwareProfile)

    def _deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                        hardwareprofile,
                                                        softwareprofile):
        """
        Raises:
            SoftwareUsesHardwareNotFound
        """

        if hardwareprofile not in softwareprofile.hardwareprofiles:
            raise SoftwareUsesHardwareNotFound(
                'Hardware profile [%s] does not belong to software'
                ' profile [%s]' % (
                    hardwareprofile.name, softwareprofile.name))

        self.getLogger().debug(
            'Deleting mapping of software profile [%s] to hardware'
            ' profile [%s]' % (softwareprofile.name, hardwareprofile.name))

        softwareprofile.hardwareprofiles.remove(hardwareprofile)

    def deleteUsableHardwareProfileFromSoftwareProfile(self, session,
                                                       hardwareProfileName,
                                                       softwareProfileName):
        """
        Delete usable hardwareProfile to softwareProfile.

        Raises:
            HardwareProfileNotFound
            SoftwareProfileNotFound
            SoftwareUsesHardwareNotFound
        """

        dbHardwareProfile = self.__getHardwareProfile(
            session, hardwareProfileName)

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        self._deleteUsableHardwareProfileFromSoftwareProfile(
            dbHardwareProfile, dbSoftwareProfile)

    def addComponentToSoftwareProfileEx(self, session, componentId,
                                        dbSoftwareProfile):
        """
        Raises:
            ComponentNotFound
        """

        dbComponent = self._componentsDbHandler.getComponentById(
            session, componentId)

        self._addComponent(dbComponent, dbSoftwareProfile)

    def _addComponent(self, dbComponent, dbSoftwareProfile):
        self.getLogger().debug(
            'Adding component [%s] to software profile [%s]' % (
                '%s-%s' % (dbComponent.name, dbComponent.version),
                dbSoftwareProfile.name))

        if dbComponent in dbSoftwareProfile.components:
            raise SoftwareProfileComponentAlreadyExists(
                'Component [%s] already enabled on software profile [%s]' % (
                    dbComponent.name, dbSoftwareProfile.name))

        dbSoftwareProfile.components.append(dbComponent)

    def addComponentToSoftwareProfile(self, session, componentId,
                                      softwareProfileId):
        """
        Add component to softwareProfile.

        Raises:
            SoftwareProfileNotFound
            ComponentNotFound
        """

        dbSoftwareProfile = self.getSoftwareProfileById(
            session, softwareProfileId)

        dbComponent = self._componentsDbHandler.getComponentById(
            session, componentId)

        self._addComponent(dbComponent, dbSoftwareProfile)

    def deleteComponentFromSoftwareProfile(self, session, componentId,
                                           softwareProfileId):
        """
        Delete component from softwareProfile.

        Raises:
            SoftwareProfileNotFound
        """

        dbSoftwareProfile = self.getSoftwareProfileById(
            session, softwareProfileId)

        dbComponent = self._componentsDbHandler.getComponentById(
            session, componentId)

        compDescr = '%s-%s' % (dbComponent.name, dbComponent.version)

        self.getLogger().debug(
            'Deleting component [%s] from software profile [%s]' % (
                compDescr, dbSoftwareProfile))

        if dbComponent not in dbSoftwareProfile.components:
            raise SoftwareProfileComponentNotFound(
                'Component [%s] not enabled on software profile [%s]' % (
                    compDescr, dbSoftwareProfile.name))

        dbSoftwareProfile.components.remove(dbComponent)

        self.getLogger().debug(
            'Deleted component [%s] from software profile [%s]' % (
                compDescr, dbSoftwareProfile.name))

    def __getPackage(self, session, packageName): \
            # pylint: disable=no-self-use
        return session.query(Package).filter(
            Package.name == packageName).one()

    def addPackageToSoftwareProfile(self, session, packageName,
                                    softwareProfileName):
        """
        Add package to software profile
        """

        self.getLogger().debug(
            'Adding package [%s] to software profile [%s]' % (
                packageName, softwareProfileName))

        # Check if package record already exists
        try:
            dbPackage = self.__getPackage(session, packageName)
        except NoResultFound:
            dbPackage = None

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        if not dbPackage:
            dbPackage = Package(packageName)

        if dbPackage in dbSoftwareProfile.packages:
            raise PackageAlreadyExists(
                'Package [%s] already exists for software'
                ' profile [%s]' % (packageName, softwareProfileName))

        self.getLogger().debug(
            'Adding package [%s] to software profile [%s]' % (
                packageName, softwareProfileName))

        dbSoftwareProfile.packages.append(dbPackage)

    def deletePackageFromSoftwareProfile(self, session, packageName,
                                         softwareProfileName):
        """
        Delete package from software profile.
        """

        self.getLogger().debug(
            'Deleting package [%s] from software profile [%s]' % (
                packageName, softwareProfileName))

        try:
            dbPackage = self.__getPackage(session, packageName)
        except NoResultFound:
            dbPackage = None

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        if dbPackage not in dbSoftwareProfile.packages:
            raise PackageNotFound(
                'Package [%s] does not exist for software profile [%s]' % (
                    packageName, softwareProfileName))

        dbSoftwareProfile.packages.remove(dbPackage)

        if not dbPackage.softwareprofiles:
            session.delete(dbPackage)

        self.getLogger().debug(
            'Deleted package [%s] from software profile ID [%s]' % (
                packageName, softwareProfileName))

    def __getPartition(self, session, name):  # pylint: disable=no-self-use
        return session.query(Partition).filter(
            Partition.name == name).one()

    def addPartitionToSoftwareProfile(self, session, partition,
                                      softwareProfileName):
        """
        Add partition to software profile.
        """

        self.getLogger().debug(
            'Adding partition [%s] to software profile [%s]' % (
                partition.getName(), softwareProfileName))

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        try:
            dbPartition = self.__getPartition(session, partition.getName())
        except NoResultFound:
            pass

        if dbPartition in dbSoftwareProfile.partitions:
            raise PartitionAlreadyExists(
                'Partition [%s] already exists for software'
                ' profile [%s]' % (
                    partition.getName(), softwareProfileName))

        dbPartition = Partition(
            name=partition.getName(),
            device=partition.getDevice(),
            mountPoint=partition.getMountPoint(),
            fsType=partition.getFsType(),
            size=partition.getSize(),
            options=partition.getOptions(),
            preserve=partition.getPreserve(),
            bootLoader=partition.getBootLoader(),
            directAttachment=partition.getDirectAttachment(),
            indirectAttachment=partition.getIndirectAttachment(),
            diskSize=partition.getDiskSize()
        )

        dbSoftwareProfile.partitions.append(dbPartition)

    def deletePartitionFromSoftwareProfile(self, session, partitionName,
                                           softwareProfileName):
        """
        Delete partition from software profile.
        """

        self.getLogger().debug(
            'Deleting partition [%s] from software profile [%s]' % (
                partitionName, softwareProfileName))

        dbSoftwareProfile = self.getSoftwareProfile(
            session, softwareProfileName)

        try:
            dbPartition = self.__getPartition(session, partitionName)
        except NoResultFound:
            raise PartitionNotFound(
                'Partition [%s] does not exist for software profile'
                ' [%s]' % (partitionName, softwareProfileName))

        self.getLogger().debug(
            'Deleted partition [%s] from software profile [%s]' % (
                partitionName, softwareProfileName))

        dbSoftwareProfile.partitions.remove(dbPartition)
