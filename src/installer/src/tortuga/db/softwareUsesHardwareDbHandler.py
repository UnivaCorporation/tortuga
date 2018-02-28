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

# pylint: disable=not-callable,,multiple-statements,no-member,no-name-in-module

from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.softwareUsesHardware import SoftwareUsesHardware
from tortuga.db.softwareProfiles import SoftwareProfiles
from tortuga.exceptions.softwareProfileNotFound \
    import SoftwareProfileNotFound


class SoftwareUsesHardwareDbHandler(TortugaDbObjectHandler):
    def getSoftwareUsesHardwareList(self, session):
        """
        Get list of all mappings
        """

        self.getLogger().debug('Retrieving all available mappings')

        return session.query(SoftwareUsesHardware).all()

    def getAllowedHardwareProfilesBySoftwareProfileName(
            self, session, softwareProfileName):
        """
        Get list of mappings for the given software profile name
        """

        self.getLogger().debug(
            'Retrieving mappings for software profile [%s]' % (
                softwareProfileName))

        try:
            dbSoftwareProfile = session.query(
                SoftwareProfiles).filter(
                    SoftwareProfiles.name == softwareProfileName).one()
        except NoResultFound:
            raise SoftwareProfileNotFound(
                'Software profile [%s] not found' % (softwareProfileName))

        return session.query(SoftwareUsesHardware).filter(
            SoftwareUsesHardware.softwareProfileId == dbSoftwareProfile.
            id).all()
