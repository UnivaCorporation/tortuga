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

from typing import Optional
from sqlalchemy.orm.session import Session

from tortuga.db.kitsDbHandler import KitsDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.kit.utils import format_kit_descriptor
from tortuga.objects.component import Component
from tortuga.objects.kit import Kit
from tortuga.objects.kitSource import KitSource
from tortuga.objects.tortugaObject import TortugaObjectList


class KitDbApi(TortugaDbApi):
    """
    Kit DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._kitsDbHandler = KitsDbHandler()

    def getKit(self, session: Session, name, version,
               iteration: Optional[str] = None):
        """
        Get kit from the db.

            Returns:
                kit
            Throws:
                KitNotFound
                DbError
        """

        try:
            dbKit = self._kitsDbHandler.getKit(
                session, name, version, iteration)

            kit = Kit.getFromDbDict(dbKit.__dict__)

            return self.__retrieveAllKitData(dbKit, kit)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def __retrieveAllKitData(self, dbKit, kit):
        """
        Retrieve full kit data from the db.
        """

        for dbComponent in dbKit.components:
            # Force loading of OS/OS familyinfo
            self.loadRelations(dbComponent, {
                'os_components': True,
                'osfamily_components': True,
            })

            # Convert into component object
            c = Component.getFromDbDict(dbComponent.__dict__)

            # Associate component with kit
            kit.addComponent(c)

        kit.setSources(self.getTortugaObjectList(KitSource, dbKit.sources))

        return kit

    def getKitById(self, session: Session, id_):
        """
        Get kit from the db

            Returns:
                kit
            Throws:
                KitNotFound
                DbError
        """

        try:
            dbKit = self._kitsDbHandler.getKitById(session, id_)
            kit = Kit.getFromDbDict(dbKit.__dict__)
            return self.__retrieveAllKitData(dbKit, kit)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def getKitList(self, session: Session,
                   os_kits_only: Optional[bool] = False):
        """
        Get list of all available or os kits only from the db
        """

        try:
            kits = []

            for kit in self._kitsDbHandler.getKitList(
                    session, os_kits_only=os_kits_only):
                self.loadRelations(kit, {'components': True})

                kits.append(Kit.getFromDbDict(kit.__dict__))

            return TortugaObjectList(kits)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def addKit(self, session: Session, kit):
        """
        Insert kit into the db.

        Raises:
            KitAlreadyExists
            DbError
        """

        try:
            dbKit = self._kitsDbHandler.addKit(session, kit)

            session.commit()

            iteration = dbKit.components[0].os_components[0].os.arch \
                if dbKit.isOs else dbKit.iteration

            kit_descr = format_kit_descriptor(
                dbKit.name, dbKit.version, iteration)

            logmsg = 'Installed OS kit [{0}] successfully' \
                if dbKit.isOs else 'Installed kit [{0}] successfully'

            self._logger.info(logmsg.format(kit_descr))
        except TortugaException:
            session.rollback()

            raise
        except Exception as ex:
            session.rollback()

            self._logger.exception(str(ex))

            raise

    def deleteKit(self, session: Session, name, version, iteration, force=False):
        """
        Delete kit from the db.

        Raises:
            KitNotFound
            KitInUse
            DbError
        """

        try:
            self._kitsDbHandler.deleteKit(
                session, name, version, iteration, force=force)

            session.commit()
        except TortugaException:
            session.rollback()

            raise
        except Exception as ex:
            session.rollback()

            self._logger.exception(str(ex))
            raise

    def addComponentsToKit(self, session: Session, kit, compList):
        """
        Add components found in compList to existing kit

            Returns:
                None
            Throws:
                KitNotFound
                KitInUse
                DbError
        """

        try:
            self._kitsDbHandler.addComponentsToKit(session, kit, compList)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise
