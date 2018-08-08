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

# pylint: disable=W0703

from tortuga.db.tortugaDbApi import TortugaDbApi
from sqlalchemy.orm.session import Session
from tortuga.db.operatingSystemsDbHandler import OperatingSystemsDbHandler
from tortuga.exceptions.tortugaException import TortugaException


class OperatingSystemDbApi(TortugaDbApi):
    """
    Currently referenced in exactly *ONE* place- primeDb.py as part
    of tortugaDeployer.py
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._osDbHandler = OperatingSystemsDbHandler()

    def addOsIfNotFound(self, session: Session, osInfo):
        dbOs = None

        try:
            dbOs = self._osDbHandler.addOsIfNotFound(session, osInfo)
            session.commit()
        except (Exception, TortugaException) as ex:
            self.getLogger().exception('%s' % (ex))

        return dbOs
