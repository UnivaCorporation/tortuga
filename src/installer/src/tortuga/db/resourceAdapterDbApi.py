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

from typing import List, Type

from sqlalchemy.orm.session import Session
from tortuga.db import resourceAdaptersDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.resourceAdapterAlreadyExists import \
    ResourceAdapterAlreadyExists
from tortuga.exceptions.resourceAdapterNotFound import ResourceAdapterNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.resourceAdapter import ResourceAdapter
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList

from .models.resourceAdapter import ResourceAdapter as ResourceAdapterModel


class ResourceAdapterDbApi(TortugaDbApi):
    def __init__(self):
        TortugaDbApi.__init__(self)

        self._resourceAdaptersDbHandler = resourceAdaptersDbHandler.\
            ResourceAdaptersDbHandler()

    def getResourceAdapter(self, session: Session, name):
        ra_obj = None

        try:
            db_ra = self._resourceAdaptersDbHandler.getResourceAdapter(
                session, name)
            self.loadRelations(db_ra, {'kit': True})
            ra_obj = ResourceAdapter.getFromDbDict(db_ra.__dict__)
            ra_obj.set_settings(db_ra.settings)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))

        return ra_obj

    def addResourceAdapter(self, session: Session, name, kitId=None):
        """
        Add resource adapter

        Raises:
            ResourceAdapterAlreadyExists
        """

        resourceAdapterObj = None

        self._logger.debug('addResourceAdapter(name=[%s])' % (name))

        try:
            self.getResourceAdapter(session, name)

            raise ResourceAdapterAlreadyExists(
                'Resource adapter [%s/%s] already exists' % (name, kitId))
        except ResourceAdapterNotFound:
            # Ok, good!
            pass

        try:
            dbResourceAdapter = self._resourceAdaptersDbHandler.\
                addResourceAdapter(session, name, kitId)

            session.commit()

            resourceAdapterObj = ResourceAdapter.getFromDbDict(
                dbResourceAdapter.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))

        # Success!
        self._logger.info('Added resource adapter [%s]' % (name))

        return resourceAdapterObj

    def deleteResourceAdapter(self, session: Session, name):
        """
        Remove resource adapter

        Raises:
        """

        self._logger.debug('deleteResourceAdapter(name=[%s])' % (name))

        try:
            self._resourceAdaptersDbHandler.deleteResourceAdapter(
                session, name)

            session.commit()
        except ResourceAdapterNotFound:
            self._logger.info(
                'Resource adapter [%s] not found' % (name))
            return
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))

        # Success!
        self._logger.info('Deleted resource adapter [%s]' % (name))

    def getResourceAdapterList(self, session: Session) -> List[ResourceAdapter]:
        try:
            db_ra_list: List[ResourceAdapterModel] = \
                self._resourceAdaptersDbHandler.getResourceAdapterList(
                    session)
            ra_list: List[ResourceAdapter] = \
                self.getTortugaObjectList(ResourceAdapter, db_ra_list)

            return ra_list

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise

    def getTortugaObjectList(self,
                             cls: Type[ResourceAdapter],
                             db_list: List[ResourceAdapterModel]
                             ) -> List[ResourceAdapter]:
        item_list: List[ResourceAdapter] = []

        for db_item in db_list:
            item: ResourceAdapter = cls.getFromDbDict(db_item.__dict__)
            item.set_settings(db_item.settings)
            item_list.append(item)

        return TortugaObjectList(item_list)
