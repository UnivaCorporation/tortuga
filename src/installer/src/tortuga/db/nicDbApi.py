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

from tortuga.db.dbManager import DbManager
from tortuga.db.nicsDbHandler import NicsDbHandler
from tortuga.exceptions.tortugaException import TortugaException


class NicDbApi(TortugaDbApi):
    """
    Nics DB API class
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._nicsDbHandler = NicsDbHandler()

    def setNicIp(self, mac, ip):
        """
        Set NIC IP in database.
        """

        try:
            session = DbManager().openSession()
            try:
                dbNics = self._nicsDbHandler.getNic(session, mac)

                self.getLogger().debug(
                    'setNicIp: mac [%s] ip [%s]' % (mac, ip))

                dbNics.ip = ip
                session.commit()
                return
            except TortugaException as ex:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise
        finally:
            DbManager().closeSession()

    def setIp(self, nicId, ip):
        try:
            session = DbManager().openSession()

            try:
                dbNic = self._nicsDbHandler.getNicById(session, nicId)

                self.getLogger().debug('setIp: nicId [%s] ip [%s]' % (
                    nicId, ip))

                dbNic.ip = ip

                session.commit()

                return
            except TortugaException as ex:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise
        finally:
            DbManager().closeSession()
