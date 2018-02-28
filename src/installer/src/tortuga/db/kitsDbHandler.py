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

# pylint: disable=not-callable,multiple-statements,no-member,no-self-use
# pylint; disable=no-name-in-module

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.kits import Kits
from tortuga.db.components import Components
from tortuga.db.operatingSystemsFamilies import OperatingSystemsFamilies
from tortuga.db.osComponents import OsComponents
from tortuga.db.osFamilyComponents import OsFamilyComponents
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.kitInUse import KitInUse
from tortuga.exceptions.kitAlreadyExists import KitAlreadyExists
from tortuga.kit.utils import format_kit_descriptor
from tortuga.config.configManager import ConfigManager


class KitsDbHandler(TortugaDbObjectHandler):
    """
    This class is meant to be used by the kit DB API. It should hide
    implementation details from the api class, but not provide any
    session/transaction management.
    """

    def getKitById(self, session, kit_id):
        """
        Get kit from the db using its id.
        """

        self.getLogger().debug('Retrieving kit id [%s]' % (kit_id))

        dbKit = session.query(Kits).get(kit_id)

        if not dbKit:
            raise KitNotFound('Kit ID [%s] not found.' % (kit_id))

        return dbKit

    def getKit(self, session, name, version, iteration=None):
        """
        Get kit from the db.
        """

        self.getLogger().debug('Retrieving kit [%s]' % (name))

        try:
            if version is not None and version is not None and \
                    iteration is not None:
                dbKitQuery = session.query(Kits).filter(
                    and_(Kits.name == name,
                         Kits.version == version,
                         Kits.iteration == iteration))
            elif version is not None:
                dbKitQuery = session.query(Kits).filter(
                    and_(Kits.name == name, Kits.version == version))
            else:
                dbKitQuery = session.query(Kits).filter(Kits.name == name)

            return dbKitQuery.one()
        except NoResultFound:
            raise KitNotFound('Kit [%s] not found' % (name))
        except MultipleResultsFound:
            raise KitNotFound(
                'Ambiguous kit specification. Specify version and/or'
                ' iteration')

    def getKitList(self, session):
        """
        Get list of kits from the db.
        """

        self.getLogger().debug('Retrieving all available kits')

        return session.query(Kits).all()

    def _getOsFamilyInfo(self, session, osFamilyName, osFamilyVersion,
                         osFamilyArch):
        """
        Return an osFamilyInfo object matching the search specifications
        """

        try:
            return session.query(OperatingSystemsFamilies).filter(and_(
                OperatingSystemsFamilies.name == osFamilyName,
                OperatingSystemsFamilies.version == osFamilyVersion,
                OperatingSystemsFamilies.arch == osFamilyArch)).one()
        except NoResultFound:
            return None

    def _initDbOsComponent(self, session, osComponent, dbComponent):
        from tortuga.db import operatingSystemsDbHandler

        _operatingSystemsDbHandler = operatingSystemsDbHandler.\
            OperatingSystemsDbHandler()

        # Create OsComponents assocation object
        dbOsComponent = OsComponents()
        dbOsComponent.os = _operatingSystemsDbHandler.\
            addOsIfNotFound(session, osComponent.getOsInfo())
        dbOsComponent.os_components = dbComponent
        session.add(dbOsComponent)

    def _initDbOsFamilyComponent(self, session, osFamilyComponent,
                                 dbComponent):
        from tortuga.db import operatingSystemsDbHandler
        _operatingSystemsDbHandler = operatingSystemsDbHandler.\
            OperatingSystemsDbHandler()

        # Create OsFamilyComponents assocation object
        dbOsFamilyComponent = OsFamilyComponents()
        dbOsFamilyComponent.family = _operatingSystemsDbHandler.\
            addOsFamilyIfNotFound(
                session, osFamilyComponent.getOsFamilyInfo())
        dbOsFamilyComponent.osfamily_components = dbComponent
        session.add(dbOsFamilyComponent)

    def _addComponentToKit(self, session, c, dbKit):
        """
        Add component to existing Kit
        """

        try:
            dbComponent = session.query(Components).join(Kits).filter(
                and_(Kits.name == dbKit.name,
                     Kits.version == dbKit.version,
                     Kits.iteration == dbKit.iteration,
                     Components.name == c.getName(),
                     Components.version == c.getVersion())).one()
        except NoResultFound:
            # Unable to find matching component, add a new one
            dbComponent = Components(name=c.getName(),
                                     version=c.getVersion(),
                                     description=c.getDescription())

            dbComponent.kit = dbKit

        # Convert OsComponent and OsFamilyComponent lists to their db
        # representation
        for osComponent in c.getOsComponentList():
            self._initDbOsComponent(session, osComponent, dbComponent)

        for osFamilyComponent in c.getOsFamilyComponentList():
            self._initDbOsFamilyComponent(
                session, osFamilyComponent, dbComponent)

        # Add component to kit
        dbKit.components.append(dbComponent)

    def addComponentsToKit(self, session, kit, compList):
        """
        Add components found in 'compList' to the kit matching the
        specified 'kit'
        """

        dbKit = session.query(Kits).filter(
            and_(Kits.name == kit.getName(),
                 Kits.version == kit.getVersion(),
                 Kits.iteration == kit.getIteration())).one()

        # Add components.
        for c in compList:
            self._addComponentToKit(session, c, dbKit)

        return dbKit

    def addKit(self, session, kit):
        """
        Insert kit into the db.

        Raises:
            KitAlreadyExists
        """

        try:
            self.getKit(
                session, kit.getName(), kit.getVersion(),
                kit.getIteration())

            raise KitAlreadyExists('Kit [%s] already exists' % (kit))
        except KitNotFound:
            # OK.
            pass

        self.getLogger().debug('Installing kit [%s]' % (kit))

        dbKit = Kits(name=kit.getName(),
                     version=kit.getVersion(),
                     iteration=kit.getIteration(),
                     description=kit.getDescription(),
                     isOs=kit.getIsOs(),
                     isRemovable=kit.getIsRemovable())

        # Add components.
        for c in kit.getComponentList():
            self._addComponentToKit(session, c, dbKit)

        # Add the newly created kit to the db session
        session.add(dbKit)

        return dbKit

    def deleteKit(self, session, name, version, iteration, force=False):
        """
        Delete kit from the db.

        Raises:
            KitNotFound
        """

        dbKit = self.getKit(session, name, version, iteration)

        # Check if kit exists, and whether it is being used.
        self.getLogger().debug(
            'Deleting kit [%s]' % (
                format_kit_descriptor(
                    dbKit.name, dbKit.version, dbKit.iteration)))

        installer = ConfigManager().getInstaller()

        for dbComponent in dbKit.components:
            if not force and dbComponent.softwareprofiles:
                softwareProfileList = [
                    dbSoftwareProfile.name
                    for dbSoftwareProfile in dbComponent.softwareprofiles]

                # If the component is associated with only one software
                # profile and that software profile contains the
                # installer node, the kit can be safely removed.
                if not (dbKit.isOs and len(softwareProfileList) == 1 and
                        dbComponent.softwareprofiles[0].nodes and
                        dbComponent.softwareprofiles[0].
                        nodes[0].name == installer):
                    raise KitInUse(
                        'Kit cannot be deleted.  Component [%s] from'
                        ' kit [%s] is in use by software profile(s):'
                        ' [%s]' % (
                            dbComponent.name,
                            format_kit_descriptor(dbKit.name, dbKit.version,
                                                  dbKit.iteration),
                            ' '.join(softwareProfileList)))

        session.delete(dbKit)

        self.getLogger().debug(
            'Marking kit [%s] for deletion' % (dbKit.name))
