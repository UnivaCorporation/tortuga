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

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.osNotFound import OsNotFound
from tortuga.helper import osHelper
from tortuga.objects.osFamilyInfo import OsFamilyInfo
from tortuga.objects.osInfo import OsInfo

from .models.operatingSystem import OperatingSystem
from .models.operatingSystemFamily import OperatingSystemFamily


class OperatingSystemsDbHandler(TortugaDbObjectHandler):
    """
    This class handles OS table.
    """

    def getOsInfo(self, session: Session, name: str,
                  vers: Optional[Union[str, None]] = None,
                  arch: Optional[Union[str, None]] = None) -> OperatingSystem: \
            # pylint: disable=no-self-use
        """
        Return osInfo for specified name/version/arch

        Raises:
            OsNotFound
        """

        if name and vers and arch:
            osFilter = and_(OperatingSystem.name == name,
                            OperatingSystem.version == vers,
                            OperatingSystem.arch == arch)
        elif name and vers:
            osFilter = and_(OperatingSystem.name == name,
                            OperatingSystem.version == vers)
        else:
            osFilter = and_(OperatingSystem.name == name)

        try:
            return session.query(OperatingSystem).filter(osFilter).one()
        except NoResultFound:
            raise OsNotFound(
                'Operating system [%s-%s-%s] not found.' % (
                    name, vers, arch))

    def getOsId(self, session: Session, name: str, version: str,
                arch: str) -> int:
        """
        Return id for the specified operating system.
        """
        return self.getOsInfo(session, name, version, arch).id

    def _getOsFamily(self, session: Session,
                     osFamilyInfo: OsFamilyInfo) -> OperatingSystemFamily: \
            # pylint: disable=no-self-use
        if osFamilyInfo.getName() and osFamilyInfo.getVersion() and \
                osFamilyInfo.getArch():
            osFamilyFilter = and_(
                OperatingSystemFamily.name == osFamilyInfo.getName(),
                OperatingSystemFamily.version == osFamilyInfo.
                getVersion(),
                OperatingSystemFamily.arch == osFamilyInfo.getArch()
            )
        elif osFamilyInfo.getName() and osFamilyInfo.getVersion():
            osFamilyFilter = and_(
                OperatingSystemFamily.name == osFamilyInfo.getName(),
                OperatingSystemFamily.version ==
                osFamilyInfo.getVersion(),
                OperatingSystemFamily.arch == None  # noqa
            )
        else:
            osFamilyFilter = and_(
                OperatingSystemFamily.name == osFamilyInfo.getName(),
                OperatingSystemFamily.version == None,  # noqa
                OperatingSystemFamily.arch == None  # noqa
            )

        try:
            return session.query(OperatingSystemFamily).filter(
                osFamilyFilter).one()
        except NoResultFound:
            pass

        return None

    def __addOsFamilyRoot(self, session: Session) -> OperatingSystemFamily: \
            # pylint: disable=no-self-use
        dbOsFamily = OperatingSystemFamily(name='root')
        session.add(dbOsFamily)
        return dbOsFamily

    def addOsFamilyIfNotFound(self, session: Session,
                              osFamilyInfo: OsFamilyInfo) -> OperatingSystemFamily:
        familyName = osFamilyInfo.getName()
        familyVers = osFamilyInfo.getVersion()
        familyArch = osFamilyInfo.getArch()

        dbOsFamily = self._getOsFamily(session, osFamilyInfo)

        if dbOsFamily:
            return dbOsFamily

        # The 'root' entry is an exception since it doesn't have a
        # parent.  Just add it...
        if familyName == 'root':
            dbOsFamily = self.__addOsFamilyRoot(session)
        else:
            # ... otherwise, check for the parent of the specified
            # and it's parent should be 'root'
            osFamilyInfoParent = OsFamilyInfo(familyName, familyVers)

            dbOsFamilyParent = self._getOsFamily(
                session, osFamilyInfoParent)

            if not dbOsFamilyParent:
                # Check for the root entry
                osFamilyInfoRoot = OsFamilyInfo('root')

                dbOsFamilyRoot = self._getOsFamily(
                    session, osFamilyInfoRoot)

                if not dbOsFamilyRoot:
                    dbOsFamilyRoot = self.__addOsFamilyRoot(session)

                dbOsFamilyParent = OperatingSystemFamily(
                    name=familyName, version=familyVers)

                session.add(dbOsFamilyParent)

                dbOsFamilyRoot.children.append(dbOsFamilyParent)

            dbOsFamily = OperatingSystemFamily(
                name=familyName,
                version=familyVers,
                arch=familyArch)

            session.add(dbOsFamily)

            dbOsFamilyParent.children.append(dbOsFamily)

        return dbOsFamily

    def addOsIfNotFound(self, session: Session, osInfo: OsInfo):
        """
        Insert operating system into the db if it is not found.
        """
        try:
            return self.getOsInfo(
                session, osInfo.getName(), osInfo.getVersion(),
                osInfo.getArch())
        except OsNotFound:
            pass

        # Translate osInfo
        tmpOsInfo = osHelper.getOsInfo(osInfo.getName(),
                                       osInfo.getVersion(),
                                       osInfo.getArch())

        # Check for existence of OS family
        dbOsFamily = self.addOsFamilyIfNotFound(
            session, tmpOsInfo.getOsFamilyInfo())

        dbOs = OperatingSystem(name=osInfo.getName(),
                               version=osInfo.getVersion(),
                               arch=osInfo.getArch())

        dbOs.family = dbOsFamily

        session.add(dbOs)

        return dbOs
