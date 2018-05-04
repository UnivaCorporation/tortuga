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

# pylint: disable=multiple-statements,no-member,not-callable

from sqlalchemy.exc import IntegrityError

from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.objects.network import Network
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.networkInUse import NetworkInUse
from tortuga.db.dbManager import DbManager


class NetworkDbApi(TortugaDbApi):
    """
    Network DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        from tortuga.db.hardwareProfilesDbHandler \
            import HardwareProfilesDbHandler
        self._hardwareProfilesDbHandler = HardwareProfilesDbHandler()
        from tortuga.db.nodesDbHandler import NodesDbHandler
        from tortuga.db.nicsDbHandler import NicsDbHandler
        from tortuga.db.networksDbHandler import NetworksDbHandler
        self._nodesDbHandler = NodesDbHandler()
        self._nicsDbHandler = NicsDbHandler()
        self._networksDbHandler = NetworksDbHandler()

    def getNetworkList(self):
        """
        Get list of networks from the db.
        """

        session = DbManager().openSession()

        try:
            dbList = self._networksDbHandler.getNetworkList(session)

            return self.getTortugaObjectList(Network, dbList)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNetwork(self, address, netmask):
        """
        Get a network from the db.
        """

        session = DbManager().openSession()

        try:
            network = self._networksDbHandler.getNetwork(
                session, address, netmask)

            return Network.getFromDbDict(network.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNetworkById(self, id_):
        """
        Get a network by id from the db.
        """

        session = DbManager().openSession()

        try:
            network = self._networksDbHandler.getNetworkById(session, id_)

            return Network.getFromDbDict(network.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def addNetwork(self, network):
        """
        Insert network into the db.

            Returns:
                networkId
            Throws:
                NetworkAlreadyExists
                DbError
        """

        session = DbManager().openSession()

        try:
            dbNetwork = self._networksDbHandler.addNetwork(
                session, network)

            session.commit()

            return dbNetwork.id
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def updateNetwork(self, network):
        """
        Updates network in DB..

            Returns:
                network
            Throws:
                NetworkNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbNetwork = self._networksDbHandler.updateNetwork(
                session, network)

            newNetwork = Network.getFromDbDict(dbNetwork.__dict__)

            session.commit()

            return newNetwork
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def deleteNetwork(self, id_):
        """
        Delete network from the db.

            Returns:
                None
            Throws:
                NetworkInUse
                NetworkNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            self._networksDbHandler.deleteNetwork(session, id_)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except IntegrityError as ex:
            raise NetworkInUse('Network is in use')
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNetworkListByType(self, type_):
        """
        Return list of networks of the given type.

            Returns:
                [networks]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            dbNetworks = self._networksDbHandler.\
                getNetworkListByType(session, type_)

            return self.getTortugaObjectList(Network, dbNetworks)
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()
