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

import socket
from typing import List, Optional, Union

from sqlalchemy.orm.session import Session

from tortuga.db.dbManager import DbManager
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.node import Node
from tortuga.objects.parameter import Parameter
from tortuga.objects.provisioningInfo import ProvisioningInfo
from tortuga.objects.tortugaObject import TortugaObjectList

from .models.node import Node as NodeModel


class NodeDbApi(TortugaDbApi):
    """
    Nodes DB API class.
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._nodesDbHandler = NodesDbHandler()
        self._globalParameterDbApi = GlobalParameterDbApi()

    def getNode(self, name: str, optionDict: Optional[Union[dict, None]] = None):
        """
        Get node from the db.

            Returns:
                node
            Throws:
                NodeNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            dbNode = self._nodesDbHandler.getNode(session, name)

            self.loadRelations(dbNode, optionDict)

            self.loadRelations(dbNode, {
                'softwareprofile': True,
                'hardwareprofile': True,
                'tags': True,
            })

            return Node.getFromDbDict(dbNode.__dict__)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNodesByAddHostSession(self, ahSession: str,
                                 optionDict: Optional[Union[dict, None]] = None) -> TortugaObjectList:
        """
        Get node(s) from db based their addhost session
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    self._nodesDbHandler.getNodesByAddHostSession(
                        session, ahSession), relations=optionDict)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNodesByNameFilter(self, nodespec: str,
                             optionDict: Optional[Union[dict, None]] = None) -> TortugaObjectList:
        """
        Get node(s) from db based on the name filter
        """

        with DbManager().session() as session:
            nodes = self.__expand_nodespec(session, nodespec)

            # ensure 'resourceadapter' relation is always loaded
            for node in nodes:
                self.loadRelation(node.hardwareprofile, 'resourceadapter')

            return self.__convert_nodes_to_TortugaObjectList(
                nodes, relations=optionDict)

    def getNodeById(self, nodeId: int, optionDict: Optional[Union[dict, None]] = None):

        session = DbManager().openSession()

        try:
            dbNode = self._nodesDbHandler.getNodeById(session, nodeId)

            self.loadRelations(dbNode, optionDict)

            return Node.getFromDbDict(dbNode.__dict__)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNodeByIp(self, ip):
        session = DbManager().openSession()

        try:
            node = self._nodesDbHandler.getNodeByIp(session, ip)

            return Node.getFromDbDict(node.__dict__)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def __convert_nodes_to_TortugaObjectList(
            self, nodes: List[NodeModel],
            relations: Optional[Union[dict, None]] = None) -> TortugaObjectList:
        """
        Return TortugaObjectList of nodes with relations populated

        :param nodes: List of Nodes objects
        :param relations: dict of relations to be loaded
        :return: TortugaObjectList
        """

        nodeList = TortugaObjectList()

        relations = relations or dict(softwareprofile=True,
                                      hardwareprofile=True)

        for t in nodes:
            self.loadRelations(t, relations)

            # Always load 'tags' relation
            self.loadRelations(t, {'tags': True})

            node = Node.getFromDbDict(t.__dict__)

            nodeList.append(node)

        return nodeList

    def getNodeList(self, tags: Optional[Union[dict, None]] = None):
        """
        Get list of all available nodes from the db.

            Returns:
                [node]
            Throws:
                DbError
        """

        session = DbManager().openSession()

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                self._nodesDbHandler.getNodeList(session, tags=tags))
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getProvisioningInfo(self, nodeName: str):
        """
        Get the provisioing information for a given provisioned address

            Returns:
                [provisioningInformation structure]
            Throws:
                NodeNotFound
                DbError
        """

        session = DbManager().openSession()

        try:
            provisioningInfo = ProvisioningInfo()

            dbNode = self._nodesDbHandler.getNode(session, nodeName)

            if dbNode.softwareprofile:
                self.loadRelations(dbNode.softwareprofile, {
                    'partitions': True,
                })

                for component in dbNode.softwareprofile.components:
                    self.loadRelations(component, {
                        'kit': True,
                        'os': True,
                        'family': True,
                        'os_components': True,
                        'osfamily_components': True,
                    })

            self.loadRelation(dbNode, 'hardwareprofile')

            provisioningInfo.setNode(
                Node.getFromDbDict(dbNode.__dict__))

            globalParameters = self._globalParameterDbApi.getParameterList()

            # manually inject value for 'installer'
            p = Parameter(name='Installer')

            hostName = socket.gethostname().split('.', 1)[0]

            if '.' in dbNode.name:
                nodeDomain = dbNode.name.split('.', 1)[1]

                priInstaller = hostName + '.%s' % (nodeDomain)
            else:
                priInstaller = hostName

            p.setValue(priInstaller)

            globalParameters.append(p)

            provisioningInfo.setGlobalParameters(globalParameters)

            return provisioningInfo
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def startupNode(self, nodespec: str,
                    remainingNodeList: Optional[Union[List[str]]] = None,
                    bootMethod: Optional[str] = 'n'):
        """
        Start Node
        """

        session = DbManager().openSession()

        try:
            dbNodes = self.__expand_nodespec(session, nodespec)

            if not dbNodes:
                raise NodeNotFound(
                    'No matching nodes for nodespec [%s]' % (nodespec))

            self._nodesDbHandler.startupNode(
                session, dbNodes, remainingNodeList=remainingNodeList or [],
                bootMethod=bootMethod)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def shutdownNode(self, nodespec: str,
                     bSoftShutdown: Optional[bool] = False):
        """
        Shutdown Node

        Raises:
            NodeNotFound
        """

        session = DbManager().openSession()

        try:
            dbNodes = self.__expand_nodespec(session, nodespec)

            if not dbNodes:
                raise NodeNotFound(
                    'No matching nodes for nodespec [%s]' % (nodespec))

            self._nodesDbHandler.shutdownNode(
                session, dbNodes, bSoftShutdown)

            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def __expand_nodespec(self, session: Session, nodespec: str):
        # Expand wildcards in nodespec. Each token in the nodespec can
        # be wildcard that expands into one or more nodes.

        filter_spec = []

        for nodespec_token in nodespec.split(','):
            # Convert shell-style wildcards into SQL wildcards
            if '*' in nodespec_token or '?' in nodespec_token:
                filter_spec.append(
                    nodespec_token.replace('*', '%').replace('?', '_'))

                continue

            # Add nodespec "AS IS"
            filter_spec.append(nodespec_token)

        return self._nodesDbHandler.getNodesByNameFilter(session, filter_spec)

    def evacuateChildren(self, nodeName: str):
        """
        Evacuate Children of node
        """

        session = DbManager().openSession()

        try:
            dbNode = self._nodesDbHandler.getNode(session, nodeName)

            self._nodesDbHandler.evacuateChildren(session, dbNode)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getChildrenList(self, nodeName):
        """
        Get children of node

        Raises:
            NodeNotFound
        """

        session = DbManager().openSession()

        try:
            dbNode = self._nodesDbHandler.getNode(session, nodeName)

            return self.getTortugaObjectList(Node, dbNode.children)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def checkpointNode(self, nodeName):
        """
        Checkpoint Node
        """

        session = DbManager().openSession()

        try:
            self._nodesDbHandler.checkpointNode(session, nodeName)
            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def revertNodeToCheckpoint(self, nodeName):
        """
        Revert Node to Checkpoint
        """

        session = DbManager().openSession()

        try:
            self._nodesDbHandler.revertNodeToCheckpoint(session, nodeName)

            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def migrateNode(self, nodeName, remainingNodeList, liveMigrate):
        """
        Migrate Node
        """

        session = DbManager().openSession()

        try:
            self._nodesDbHandler.migrateNode(
                session, nodeName, remainingNodeList, liveMigrate)

            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def setParentNode(self, nodeName, parentNodeName):
        '''
        Raises:
            NodeNotFound
        '''

        session = DbManager().openSession()

        try:
            dbNode = self._nodesDbHandler.getNode(session, nodeName)

            # Setting the parent to 'None' is equivalent to unsetting it
            dbNode.parentnode = self._nodesDbHandler.getNode(
                session, parentNodeName) if parentNodeName else None

            session.commit()
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def getNodesByNodeState(self, state):
        session = DbManager().openSession()

        try:
            return self.getTortugaObjectList(
                Node, self._nodesDbHandler.getNodesByNodeState(session, state))
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise
        finally:
            DbManager().closeSession()
