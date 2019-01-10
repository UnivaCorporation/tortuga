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

from sqlalchemy.orm.session import Session
from tortuga.db.componentsDbHandler import ComponentsDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.component import Component
from tortuga.objects.osInfo import OsInfo


class ComponentDbApi(TortugaDbApi):
    """
    Component DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()
        self._componentsDbHandler = ComponentsDbHandler()

    def getComponent(self, session: Session, name: str, version: str,
                     osInfo: OsInfo,
                     optionDict: Optional[Union[dict, None]] = None) \
            -> Component:
        """
        Get component from the db.

            Returns:
                component
            Throws:
                ComponentNotFound
                DbError
        """
        try:
            dbComponent = self._componentsDbHandler.getComponentByOsInfo(
                session, name, version, osInfo)

            self.loadRelations(dbComponent, optionDict)

            return Component.getFromDbDict(dbComponent.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise

    def getBestMatchComponent(self, session: Session, name, version, osInfo,
                              kitId):
        """
        Get component from the db.

            Returns:
                component
            Throws:
                ComponentNotFound
                DbError
        """

        try:
            dbComponent = self._componentsDbHandler.getBestMatchComponent(
                session, name, version, osInfo, kitId)

            self.loadRelations(dbComponent, {
                'os': True,
                'family': True,
                'kit': True,
                'os_components': True,
                'osfamily_components': True,
            })

            return Component.getFromDbDict(dbComponent.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise

    def addComponentToSoftwareProfile(self, session: Session, componentId,
                                      softwareProfileId):
        """
        Add component to softwareProfile.

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                ComponentNotFound
                SoftwareProfileComponentAlreadyExists
                DbError
        """

        try:
            self._softwareProfilesDbHandler.addComponentToSoftwareProfile(
                session, componentId, softwareProfileId)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception('%s' % ex)
            raise

    def deleteComponentFromSoftwareProfile(self, session: Session,
                                           componentId,
                                           softwareProfileId):
        """
        Delete component to software profile.

            Returns:
                None
            Throws:
                SoftwareProfileNotFound
                ComponentNotFound
                SoftwareProfileComponentNotFound
                DbError
        """

        try:
            self._softwareProfilesDbHandler.\
                deleteComponentFromSoftwareProfile(
                    session, componentId, softwareProfileId)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception('%s' % ex)
            raise

    def getComponentList(self, session: Session, softwareProfile=None):
        try:
            if softwareProfile:
                return self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, softwareProfile).components

            # List all components
            self._logger.debug('Retrieving component list')

            dbComps = self._componentsDbHandler.getComponentList(session)

            return self.getTortugaObjectList(Component, dbComps)
        except Exception as ex:
            self._logger.exception('%s' % ex)
            raise
