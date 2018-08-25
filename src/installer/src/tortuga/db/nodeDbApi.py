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

from typing import Dict, List, Optional

from sqlalchemy.orm.session import Session
from tortuga.config.configManager import getfqdn
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.node import state
from tortuga.objects.node import Node
from tortuga.objects.parameter import Parameter
from tortuga.objects.provisioningInfo import ProvisioningInfo
from tortuga.objects.tortugaObject import TortugaObjectList

from .globalParameterDbApi import GlobalParameterDbApi
from .models.node import Node as NodeModel
from .nodesDbHandler import NodesDbHandler
from .tortugaDbApi import TortugaDbApi


OptionsDict = Dict[str, bool]


class NodeDbApi(TortugaDbApi):
    """
    Nodes DB API class.
    """

    def __init__(self):
        super().__init__()

        self._nodesDbHandler = NodesDbHandler()
        self._globalParameterDbApi = GlobalParameterDbApi()

    def getNode(self, session, name: str,
                optionDict: OptionsDict = None) -> Node:
        """
        Get node from the db.

            Returns:
                node
            Throws:
                NodeNotFound
                DbError
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                [self._nodesDbHandler.getNode(session, name)],
                optionDict=optionDict)[0]
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getNodesByAddHostSession(self, session, ahSession: str,
                                 optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get node(s) from db based their addhost session
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                self._nodesDbHandler.getNodesByAddHostSession(
                    session, ahSession), optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getNodesByNameFilter(self, session, nodespec: str,
                             optionDict: OptionsDict = None,
                             include_installer: Optional[bool] = True) \
            -> TortugaObjectList:
        """
        Get node(s) from db based on the name filter; set 'include_installer'
        to False to exclude installer node from results.
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                self._nodesDbHandler.expand_nodespec(
                    session,
                    nodespec,
                    include_installer=include_installer),
                optionDict=optionDict)
        except Exception as ex:
            if not isinstance(ex, TortugaException):
                self.getLogger().exception('%s' % ex)

            raise

    def getNodeById(self, session, nodeId: int,
                    optionDict: OptionsDict = None) \
            -> Node:
        """
        Get node by id
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                [self._nodesDbHandler.getNodeById(
                    session, nodeId)], optionDict=optionDict)[0]
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getNodeByIp(self, session, ip: str,
                    optionDict: OptionsDict = None) -> Node:
        """
        Get node by ip
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                [self._nodesDbHandler.getNodeByIp(
                    session, ip)], optionDict=optionDict)[0]
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def __convert_nodes_to_TortugaObjectList(self, nodes: List[NodeModel],
                                             optionDict: OptionsDict = None,
                                             deleting: bool = True
                                             ) -> TortugaObjectList:
        """
        Return TortugaObjectList of nodes with relations populated

        :param nodes:      list of Node objects
        :param optionDict:
        :param deleting:   whether or not to include nodes in the deleting
                           state

        :return: TortugaObjectList

        """
        nodeList = TortugaObjectList()

        for node in nodes:
            #
            # Don't include nodes in the deleting state if deleting=False
            #
            if not deleting and node.state.startswith(state.DELETING_PREFIX):
                continue

            self.loadRelations(node, optionDict)

            # ensure 'resourceadapter' relation is always loaded. This one
            # is special since it's a relationship inside of a relationship.
            # It needs to be explicitly defined.
            self.loadRelation(node.hardwareprofile, 'resourceadapter')

            nodeList.append(Node.getFromDbDict(node.__dict__))

        return nodeList

    def getNodeList(self, session, tags: Optional[dict] = None,
                    optionDict: OptionsDict = None,
                    deleting: bool = False) \
            -> TortugaObjectList:
        """
        Get list of all available nodes from the db.

            Returns:
                [node]
            Throws:
                DbError
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                self._nodesDbHandler.getNodeList(session, tags=tags),
                optionDict=optionDict,
                deleting=deleting
            )
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getProvisioningInfo(self, session: Session, nodeName: str) \
            -> ProvisioningInfo:
        """
        Get the provisioing information for a given provisioned address

            Returns:
                [provisioningInformation structure]
            Throws:
                NodeNotFound
                DbError
        """

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

            globalParameters = \
                self._globalParameterDbApi.getParameterList(session)

            # manually inject value for 'installer'
            p = Parameter(name='Installer')

            hostName = getfqdn().split('.', 1)[0]

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

    def getNodesByNodeState(self, session, node_state: str,
                            optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get nodes by node state
        """

        try:
            return self.__convert_nodes_to_TortugaObjectList(
                self._nodesDbHandler.getNodesByNodeState(
                    session, node_state), optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise
