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
from tortuga.db.networkDevices import NetworkDevices
from tortuga.exceptions.networkDeviceNotFound import NetworkDeviceNotFound


class NetworkDevicesDbHandler(TortugaDbObjectHandler):
    def getNetworkDevice(self, session, name): \
            # pylint: disable=no-self-use
        try:
            return session.query(
                NetworkDevices).filter(NetworkDevices.name == name).one()
        except NoResultFound:
            raise NetworkDeviceNotFound(
                'Network device [%s] not found' % (name))

    def createNetworkDeviceIfNotExists(self, session, name):
        """
        Returns 'NetworkDevices' instance
        """

        try:
            return self.getNetworkDevice(session, name)
        except NetworkDeviceNotFound:
            pass

        # Create new NetworkDevices entry

        dbNetworkDevice = NetworkDevices(name=name)

        session.add(dbNetworkDevice)

        return dbNetworkDevice
