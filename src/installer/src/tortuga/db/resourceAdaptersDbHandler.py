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

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.resourceAdapters import ResourceAdapters
from tortuga.exceptions.resourceAdapterNotFound \
    import ResourceAdapterNotFound
from tortuga.exceptions.resourceAdapterInUse import ResourceAdapterInUse


class ResourceAdaptersDbHandler(TortugaDbObjectHandler):
    def addResourceAdapter(self, session, name, kitId): \
            # pylint: disable=unused-argument,no-self-use
        dbResourceAdapter = ResourceAdapters(name, kitId)
        session.add(dbResourceAdapter)
        return dbResourceAdapter

    def getResourceAdapter(self, session, name):
        """
        Raises:
            ResourceAdapterNotFound
        """

        try:
            self.getLogger().debug(
                'Retrieving resource adapter [%s]' % (name))

            # Resource adapters are named uniquely
            return session.query(ResourceAdapters).filter(
                ResourceAdapters.name == name).one()
        except NoResultFound:
            raise ResourceAdapterNotFound(
                'Resource adapter [%s] not found' % (name))

    def deleteResourceAdapter(self, session, name):
        """
        Raises:
            ResourceAdapterNotFound
        """

        dbResourceAdapter = self.getResourceAdapter(session, name)

        hardwareProfiles = []

        for dbHardwareProfile in dbResourceAdapter.hardwareprofiles:
            if dbHardwareProfile.nodes:
                hardwareProfiles.append(dbHardwareProfile.name)

        if hardwareProfiles:
            raise ResourceAdapterInUse(
                'Resource adapter [%s] currently in use by hardware'
                ' profile(s): %s' % (' '.join(hardwareProfiles)))

        session.delete(dbResourceAdapter)

    def getResourceAdapterList(self, session): \
            # pylint: disable=unused-argument,no-self-use
        return session.query(ResourceAdapters).all()
