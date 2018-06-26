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

from typing import List

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.networkDeviceNotFound import NetworkDeviceNotFound

from .models.networkDevice import NetworkDevice


class NetworkDevicesDbHandler(TortugaDbObjectHandler):
    def getNetworkDevice(self, session: Session, name: str) -> NetworkDevice: \
            # pylint: disable=no-self-use
        """
        Raises:
            NetworkDeviceNotFound
        """
        try:
            return session.query(
                NetworkDevice).filter(NetworkDevice.name == name).one()
        except NoResultFound:
            raise NetworkDeviceNotFound(
                'Network device [%s] not found' % (name))

    def get_network_device(self, session: Session, name: str) -> NetworkDevice:
        return session.query(NetworkDevice).filter(
            NetworkDevice.name == name).one_or_none()

    def get_network_devices(self, session: Session) \
            -> List[NetworkDevice]:  # pylint: disable=no-self-use
        """
        Return list of all network devices
        """

        return session.query(NetworkDevice).all()

    def createNetworkDeviceIfNotExists(self, session: Session, name: str) \
            -> NetworkDevice:
        """
        Return existing NetworkDevice, otherwise create new and add to
        session.
        """

        network_device = self.get_network_device(session, name)
        if network_device:
            return network_device

        return NetworkDevice(name=name)
