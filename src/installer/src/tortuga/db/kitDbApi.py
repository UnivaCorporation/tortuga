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

from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.db.kitsDbHandler import KitsDbHandler
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.kit import Kit
from tortuga.objects.component import Component
from tortuga.db.dbManager import DbManager
from tortuga.objects.kitSource import KitSource
from tortuga.kit.utils import format_kit_descriptor
from tortuga.objects.tortugaObject import TortugaObjectList


class KitDbApi(TortugaDbApi):
    """
    Kit DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._kitsDbHandler = KitsDbHandler()

    def getKit(self, name, version, iteration=None):
        """
        Get kit from the db.

            Returns:
                kit
            Throws:
                KitNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbKit = self._kitsDbHandler.getKit(
                session, name, version, iteration)

            kit = Kit.getFromDbDict(dbKit.__dict__)

            return self.__retrieveAllKitData(dbKit, kit)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

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

    def getKitById(self, id_):
        """
        Get kit from the db

            Returns:
                kit
            Throws:
                KitNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbKit = self._kitsDbHandler.getKitById(session, id_)
            kit = Kit.getFromDbDict(dbKit.__dict__)
            return self.__retrieveAllKitData(dbKit, kit)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getKitList(self):
        """
        Get list of all available kits from the db.
        """

        session = DbManager().openSession()

        try:
            kits = []

            for kit in self._kitsDbHandler.getKitList(session):
                self.loadRelations(kit, {'components': True})

                kits.append(Kit.getFromDbDict(kit.__dict__))

            return TortugaObjectList(kits)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise
        finally:
            DbManager().closeSession()

    def addKit(self, kit):
        """
        Insert kit into the db.

        Raises:
            KitAlreadyExists
            DbError
        """

        session = DbManager().openSession()

        try:
            dbKit = self._kitsDbHandler.addKit(session, kit)

            session.commit()

            iteration = dbKit.components[0].os_components[0].os.arch \
                if dbKit.isOs else dbKit.iteration

            kit_descr = format_kit_descriptor(
                dbKit.name, dbKit.version, iteration)

            logmsg = 'Installed OS kit [{0}] successfully' \
                if dbKit.isOs else 'Installed kit [{0}] successfully'

            self.getLogger().info(logmsg.format(kit_descr))
        except TortugaException:
            session.rollback()

            raise
        except Exception as exc:
            session.rollback()

            self.getLogger().exception('%s' % (exc))

            raise
        finally:
            DbManager().closeSession()

    def deleteKit(self, name, version, iteration, force=False):
        """
        Delete kit from the db.

        Raises:
            KitNotFound
            KitInUse
            DbError
        """

        session = DbManager().openSession()

        try:
            self._kitsDbHandler.deleteKit(
                session, name, version, iteration, force=force)

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

    def addComponentsToKit(self, kit, compList):
        """
        Add components found in compList to existing kit

            Returns:
                None
            Throws:
                KitNotFound
                KitInUse
                DbError
        """

        session = DbManager().openSession()

        try:
            self._kitsDbHandler.addComponentsToKit(session, kit, compList)

            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()
