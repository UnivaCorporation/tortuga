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

# pylint: disable=not-callable,multiple-statements,no-member,no-self-use

from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.networkDevicesDbHandler import NetworkDevicesDbHandler
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.nicAlreadyExists import NicAlreadyExists
from tortuga.exceptions.nicNotFound import NicNotFound

from .models.nic import Nic


class NicsDbHandler(TortugaDbObjectHandler):
    """
    This class handles nics table.
    """

    def __init__(self):
        TortugaDbObjectHandler.__init__(self)

        self._networkDevicesDbHandler = NetworkDevicesDbHandler()

    def getNic(self, session, mac):
        """
        Return nic.

        This method should be named 'getNicByMAC()'
        """

        self.getLogger().debug(
            'Retrieving NIC with MAC address [%s]' % (mac))

        try:
            return session.query(Nic).filter(Nic.mac == mac).one()
        except NoResultFound:
            raise NicNotFound(
                'NIC with MAC address [%s] not found.' % (mac))

    def getNicById(self, session, _id):
        """
        Return nic.
        """

        self.getLogger().debug('Retrieving NIC ID [%s]' % _id)

        dbNic = session.query(Nic).get(_id)

        if not dbNic:
            raise NicNotFound('NIC ID [%s] not found.' % (_id))

        return dbNic

    def addNic(self, session, nic):
        """
        Insert nic into the db.
        """

        if nic.getMac():
            self.getLogger().debug('Inserting NIC [%s]' % (nic))

            try:
                self.getNic(session, nic.getMac())

                raise NicAlreadyExists('NIC [%s] already exists' % (nic))
            except NicNotFound:
                # OK.
                pass

        dbNic = Nic(
            mac=nic.getMac(),
            nodeId=nic.getNodeId(),
            networkId=nic.getNetworkId(),
            ip=nic.getIp(),
            boot=nic.getBoot())

        dbNic.networkdevice = \
            self._networkDevicesDbHandler.createNetworkDeviceIfNotExists(
                session, nic.getNetworkDevice().getName())

        return dbNic
