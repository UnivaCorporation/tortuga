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

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.networkNotFound import NetworkNotFound

from .models.network import Network


class NetworksDbHandler(TortugaDbObjectHandler):
    """
    This class handles networks table.
    """

    def getNetwork(self, session: Session, address: str,
                   netmask: str) -> Network:
        """
        Return network.

        Raises:
            NetworkNotFound
        """

        try:
            return session.query(Network).filter(
                and_(Network.address == address,
                     Network.netmask == netmask)).one()
        except NoResultFound:
            raise NetworkNotFound(
                'Network [%s/%s] not found.' % (address, netmask))

    def getNetworkById(self, session: Session, _id: int) -> Network:
        """
        Return network.

        Raises:
            NetworkNotFound
        """

        dbNetwork = session.query(Network).get(_id)

        if not dbNetwork:
            raise NetworkNotFound('Network ID [%s] not found.' % (_id))

        return dbNetwork

    def getNetworkList(self, session: Session) -> List[Network]:
        """
        Get list of networks from the db.
        """

        return session.query(Network).all()
