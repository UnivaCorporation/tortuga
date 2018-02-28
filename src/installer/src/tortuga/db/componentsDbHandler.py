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

# pylint: disable=not-callable,multiple-statements,no-self-use,no-member

from sqlalchemy import and_, or_
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.components import Components
from tortuga.exceptions.componentAlreadyExists import ComponentAlreadyExists
from tortuga.exceptions.componentNotFound import ComponentNotFound
from tortuga.db.operatingSystems import OperatingSystems
from tortuga.db.operatingSystemsFamilies import OperatingSystemsFamilies
from tortuga.helper import osHelper


class ComponentsDbHandler(TortugaDbObjectHandler):
    """
    This class handles components table.
    """

    def getComponentById(self, session, _id):
        """
        Raises:
            ComponentNotFound
        """

        dbComponent = session.query(Components).get(_id)

        if not dbComponent:
            raise ComponentNotFound('Component ID [%d] not found' % (_id))

        return dbComponent

    def getComponentByOsInfo(self, session, name, version, osInfo):
        """
        Raises:
            ComponentNotFound
        """

        try:
            return session.query(Components).filter(
                and_(Components.name == name,
                     Components.version == version,
                     Components.os.any(name=osInfo.getName(),
                                       version=osInfo.getVersion(),
                                       arch=osInfo.getArch()))
            ).one()
        except NoResultFound:
            raise ComponentNotFound(
                'Component [%s-%s] (%s) not found.' % (
                    name, version, osInfo))

    def getComponentByOsFamilyInfo(self, session, name, version,
                                   osFamilyInfo):
        try:
            return session.query(
                Components).filter(
                    and_(
                        Components.name == name,
                        Components.version == version,
                        Components.family.any(
                            name=osFamilyInfo.getName(),
                            version=osFamilyInfo.getVersion(),
                            arch=osFamilyInfo.getArch()))).one()
        except NoResultFound:
            raise ComponentNotFound(
                'Component [%s-%s] (%s) not found.' % (
                    name, version, osFamilyInfo))

    def getBestMatchComponent(self, session, name, version, osInfo, kitId):
        """
        Return best match component

        The query will search for an exact or family match.
        """

        self.getLogger().debug(
            'Retrieving best match component for %s-%s (%s)' % (
                name, version, osInfo))

        osConfig = osHelper.getOsInfo(
            osInfo.getName(), osInfo.getVersion(), osInfo.getArch())

        matchSpec = or_(
            Components.os.any(
                name=osInfo.getName(),
                version=osInfo.getVersion(),
                arch=osInfo.getArch()),
            Components.family.any(
                name=osConfig.getOsFamilyInfo().getName(),
                version=osConfig.getOsFamilyInfo().getVersion(),
                arch=osInfo.getArch()),
            Components.family.any(
                name=osConfig.getOsFamilyInfo().getName(),
                version=osConfig.getOsFamilyInfo().getVersion(),
                arch=None),
            Components.family.any(name='root')
        )

        if version:
            filter_spec = and_(Components.kitId == kitId,
                               Components.name == name,
                               Components.version == version, matchSpec)
        else:
            filter_spec = and_(Components.kitId == kitId,
                               Components.name == name, matchSpec)

        dbComponent = session.query(Components).filter(filter_spec).first()

        if not dbComponent:
            comp_label = '%s-%s' % (name, version) if version else name

            excmsg = 'Component %s (%s) is not found.' % (comp_label, osInfo)

            raise ComponentNotFound(excmsg)

        return dbComponent

    def getComponentList(self, session):
        """
        Get list of components from the db.
        """

        self.getLogger().debug('Retrieving component list')

        return session.query(Components).all()

    def getEnabledComponentList(self, session):
        """
        Get list of components from the db that are enabled.
        """

        self.getLogger().debug('Retrieving enabled component list')

        return session.query(
            Components).filter(Components.softwareprofiles.any()).all()

    def getComponentFromComponentObject(self, session, component):
        for osInfo in component.getOsInfoList():
            self.getComponentByOsInfo(
                session, component.getName(), component.getVersion(),
                osInfo)

            break
        else:
            for osFamilyInfo in component.getOsFamilyInfoList():
                self.getComponentByOsFamilyInfo(
                    session, Components.name == component.getName(),
                    Components.version == component.getVersion(),
                    osFamilyInfo)

    def addComponent(self, session, component):
        """
        Insert component into the db.
        """

        self.getLogger().info('Inserting component [%s]' % (component))

        try:
            # Check if component already exists...
            self.getComponentFromComponentObject(session, component)

            raise ComponentAlreadyExists(
                'Component %s already exists' % (component))
        except NoResultFound:
            # OK.
            pass

        dbComponent = Components(
            name=component.getName(),
            version=component.getVersion(),
            kitId=component.getKitId(),
            description=component.getDescription())

        # Components can have either an associated operating system or
        # an association with an operating system family
        for osInfo in component.getOsInfoList():
            dbComponent.os.append(
                OperatingSystems(
                    name=osInfo.getName(),
                    version=osInfo.getVersion(),
                    arch=osInfo.getArch()
                )
            )

        for osFamilyInfo in component.getOsFamilyInfoList():
            dbComponent.family.append(
                OperatingSystemsFamilies(
                    name=osFamilyInfo.getName(),
                    version=osFamilyInfo.getVersion(),
                    arch=osFamilyInfo.getArch()
                )
            )

        session.add(dbComponent)
        session.query(func.max(Components.id)).one()
        self.getLogger().info('Inserted component id %s' % dbComponent.id)

        return dbComponent
