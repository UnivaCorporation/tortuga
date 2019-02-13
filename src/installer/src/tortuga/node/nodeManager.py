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

# pylint: disable=no-self-use,no-member,no-name-in-module

import datetime
import json
import logging
import time
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

from sqlalchemy.orm.session import Session

from tortuga.addhost.addHostManager import AddHostManager
from tortuga.addhost.addHostServerLocal import AddHostServerLocal
from tortuga.config.configManager import ConfigManager
from tortuga.db.models.hardwareProfile import \
    HardwareProfile as HardwareProfileModel
from tortuga.db.models.node import Node as NodeModel
from tortuga.db.models.nodeRequest import NodeRequest
from tortuga.db.models.nodeTag import NodeTag as NodeTagModel
from tortuga.db.models.softwareProfile import \
    SoftwareProfile as SoftwareProfileModel
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.events.types import NodeStateChanged
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.kit.actions import KitActionsManager
from tortuga.logging import NODE_NAMESPACE
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.schema import NodeSchema
from tortuga.softwareprofile.softwareProfileManager import \
    SoftwareProfileManager
from tortuga.sync.syncApi import SyncApi

from . import state


OptionDict = Dict[str, bool]


class NodeManager(TortugaObjectManager): \
        # pylint: disable=too-many-public-methods

    def __init__(self):
        super(NodeManager, self).__init__()

        self._nodeDbApi = NodeDbApi()
        self._cm = ConfigManager()
        self._bhm = osUtility.getOsObjectFactory().getOsBootHostManager(
            self._cm)
        self._syncApi = SyncApi()
        self._nodesDbHandler = NodesDbHandler()
        self._addHostManager = AddHostManager()
        self._logger = logging.getLogger(NODE_NAMESPACE)

    def __validateHostName(self, hostname: str, name_format: str) -> None:
        """
        Raises:
            ConfigurationError
        """

        bWildcardNameFormat = (name_format == '*')

        if hostname and not bWildcardNameFormat:
            # Host name specified, but hardware profile does not
            # allow setting the host name
            raise ConfigurationError(
                'Hardware profile does not allow setting host names'
                ' of imported nodes')
        elif not hostname and bWildcardNameFormat:
            # Host name not specified but hardware profile expects it
            raise ConfigurationError(
                'Hardware profile requires host names to be set')

    def createNewNode(self, session: Session, addNodeRequest: dict,
                      dbHardwareProfile: HardwareProfileModel,
                      dbSoftwareProfile: Optional[SoftwareProfileModel] = None,
                      validateIp: bool = True, bGenerateIp: bool = True,
                      dns_zone: Optional[str] = None) -> NodeModel:
        """
        Convert the addNodeRequest into a Nodes object

        Raises:
            NicNotFound
        """

        self._logger.debug(
            'createNewNode(): session=[%s], addNodeRequest=[%s],'
            ' dbHardwareProfile=[%s], dbSoftwareProfile=[%s],'
            ' validateIp=[%s], bGenerateIp=[%s]' % (
                id(session),
                addNodeRequest,
                dbHardwareProfile.name,
                dbSoftwareProfile.name if dbSoftwareProfile else '(none)',
                validateIp, bGenerateIp))

        hostname = addNodeRequest['name'] \
            if 'name' in addNodeRequest else None

        # Ensure no conflicting options (ie. specifying host name for
        # hardware profile in which host names are generated)
        self.__validateHostName(hostname, dbHardwareProfile.nameFormat)

        node = NodeModel(name=hostname)

        if 'rack' in addNodeRequest:
            node.rack = addNodeRequest['rack']

        node.addHostSession = addNodeRequest['addHostSession']

        # Complete initialization of new node record
        nic_defs = addNodeRequest['nics'] \
            if 'nics' in addNodeRequest else []

        AddHostServerLocal().initializeNode(
            session, node, dbHardwareProfile, dbSoftwareProfile, nic_defs,
            bValidateIp=validateIp, bGenerateIp=bGenerateIp,
            dns_zone=dns_zone)

        # Set hardware profile of new node
        node.hardwareprofile = dbHardwareProfile

        node.softwareprofile = dbSoftwareProfile

        # Return the new node
        return node

    def getNode(self, session: Session, name, optionDict: OptionDict = None) \
            -> Node:
        """
        Get node by name

        Raises:
            NodeNotFound
        """

        return self.__populate_nodes(
            session,
            [self._nodeDbApi.getNode(
                session, name,
                optionDict=get_default_relations(optionDict))])[0]

    def getNodeById(self, session: Session, nodeId: int,
                    optionDict: OptionDict = None) -> Node:
        """
        Get node by node id

        Raises:
            NodeNotFound
        """

        return self.__populate_nodes(
            session,
            [self._nodeDbApi.getNodeById(
                session,
                int(nodeId),
                optionDict=get_default_relations(optionDict))])[0]

    def getNodeByIp(self, session: Session, ip: str,
                    optionDict: Dict[str, bool] = None) -> Node:
        """
        Get node by IP address

        Raises:
            NodeNotFound
        """

        return self.__populate_nodes(
            session,
            [self._nodeDbApi.getNodeByIp(
                session,
                ip,
                optionDict=get_default_relations(optionDict))])[0]

    def getNodeList(self, session, tags=None,
                    optionDict: Optional[OptionDict] = None) -> List[Node]:
        """
        Return all nodes

        """
        return self.__populate_nodes(
            session,
            self._nodeDbApi.getNodeList(
                session,
                tags=tags,
                optionDict=get_default_relations(optionDict)
            )
        )

    def __populate_nodes(self, session: Session, nodes: List[Node]) \
            -> List[Node]:
        """
        Expand non-database fields in Node objects

        """

        class SoftwareProfileMetadataCache(defaultdict):
            def __missing__(self, key):
                metadata = \
                    SoftwareProfileManager().get_software_profile_metadata(
                        session, key
                    )

                self[key] = metadata

                return metadata

        swprofile_map = SoftwareProfileMetadataCache()

        for node in nodes:
            if not node.getSoftwareProfile():
                continue

            node.getSoftwareProfile().setMetadata(
                swprofile_map[node.getSoftwareProfile().getName()]
            )

        return nodes

    def updateNode(self, session: Session, nodeName: str,
                   updateNodeRequest: dict) -> None:
        """
        Calls updateNode() method of resource adapter
        """

        self._logger.debug('updateNode(): name=[{0}]'.format(nodeName))

        try:
            node = self._nodesDbHandler.getNode(session, nodeName)

            if 'nics' in updateNodeRequest:
                nic = updateNodeRequest['nics'][0]

                if 'ip' in nic:
                    node.nics[0].ip = nic['ip']
                    node.nics[0].boot = True

            # Call resource adapter
            # self._nodesDbHandler.updateNode(session, node, updateNodeRequest)

            adapter = self.__getResourceAdapter(node.hardwareprofile)

            adapter.updateNode(session, node, updateNodeRequest)

            run_post_install = False

            #
            # Capture previous state and node data as dict for firing the
            # event later on
            #
            previous_state = node.state
            node_dict = Node.getFromDbDict(node.__dict__).getCleanDict()

            if 'state' in updateNodeRequest:
                run_post_install = \
                    node.state == state.NODE_STATE_ALLOCATED and \
                    updateNodeRequest['state'] == state.NODE_STATE_PROVISIONED

                node.state = updateNodeRequest['state']
                node_dict['state'] = updateNodeRequest['state']

            session.commit()

            #
            # If the node state has changed, then fire the node state changed
            # event
            #
            if node_dict['state'] != previous_state:
                NodeStateChanged.fire(node=node_dict,
                                      previous_state=previous_state)

            if run_post_install:
                self._logger.debug(
                    'updateNode(): run-post-install for node [{0}]'.format(
                        node.name))

                self.__scheduleUpdate()
        except Exception:
            session.rollback()

            raise

    def updateNodeStatus(self, session: Session, nodeName: str,
                         node_state: Optional[str] = None,
                         bootFrom: int = None):
        """Update node status

        If neither 'state' nor 'bootFrom' are not None, this operation will
        update only the 'lastUpdated' timestamp.

        Returns:
            bool indicating whether state and/or bootFrom differed from
            current value
        """

        value = 'None' if bootFrom is None else \
            '1 (disk)' if int(bootFrom) == 1 else '0 (network)'

        self._logger.debug(
            'updateNodeStatus(): node=[%s], node_state=[{%s}],'
            ' bootFrom=[{%s}]', nodeName, node_state, value
        )

        dbNode = self._nodesDbHandler.getNode(session, nodeName)

        #
        # Capture previous state and node data in dict form for the
        # event later on
        #
        previous_state = dbNode.state
        node_dict = Node.getFromDbDict(dbNode.__dict__).getCleanDict()

        # Bitfield representing node changes (0 = state change,
        # 1 = bootFrom # change)
        changed = 0

        if node_state is not None and node_state != dbNode.state:
            # 'state' changed
            changed |= 1

        if bootFrom is not None and bootFrom != dbNode.bootFrom:
            # 'bootFrom' changed
            changed |= 2

        if changed:
            # Create custom log message
            msg = 'Node [%s] state change:' % (dbNode.name)

            if changed & 1:
                msg += ' state: [%s] -> [%s]' % (dbNode.state, node_state)

                dbNode.state = node_state
                node_dict['state'] = node_state

            if changed & 2:
                msg += ' bootFrom: [%d] -> [%d]' % (
                    dbNode.bootFrom, bootFrom)

                dbNode.bootFrom = bootFrom

            self._logger.info(msg)
        else:
            self._logger.info(
                'Updated timestamp for node [%s]' % (dbNode.name))

        dbNode.lastUpdate = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        result = bool(changed)

        # Only change local boot configuration if the hardware profile is
        # not marked as 'remote' and we're not acting on the installer
        # node.
        if dbNode.softwareprofile and \
                dbNode.softwareprofile.type != 'installer' and \
                dbNode.hardwareprofile.location != 'remote':
            # update local boot configuration for on-premise nodes
            self._bhm.writePXEFile(session, dbNode, localboot=bootFrom)

        session.commit()

        #
        # If the node state has changed, fire the node state changed
        # event
        #
        if state and (previous_state != state):
            NodeStateChanged.fire(node=node_dict,
                                  previous_state=previous_state)

        return result

    def __get_nodes_for_deletion(self, session: Session, nodespec: str,
                                 force: bool) -> List[NodeModel]:
        """
        :raises NodeNotFound:
        """
        nodes = self._nodesDbHandler.expand_nodespec(
            session, nodespec, include_installer=False)
        if not nodes:
            raise NodeNotFound(
                'No nodes matching nodespec [%s]', nodespec
            )

        # ensure nodes aren't locked
        self.__validate_delete_nodes_request(nodes, force)

        return nodes

    def deleteNode(self, session, nodespec: str, force: bool = False):
        """Delete nodes by nodespec

        :raises NodeNotFound: no matching nodes for nodespec
        """

        try:
            nodes = self.__get_nodes_for_deletion(session, nodespec, force)

            kitmgr = KitActionsManager()
            kitmgr.session = session

            # perform actual node deletion
            self.__delete_nodes(session, kitmgr, nodes)
        except Exception:
            session.rollback()

            raise

    def __validate_delete_nodes_request(self, nodes: List[NodeModel],
                                        force: bool):
        """
        Raises:
            DeleteNodeFailed
        """

        swprofile_distribution: Dict[SoftwareProfileModel, int] = {}

        for node in nodes:
            if node.softwareprofile not in swprofile_distribution:
                swprofile_distribution[node.softwareprofile] = 0

            swprofile_distribution[node.softwareprofile] += 1

        errors: List[str] = []

        for software_profile, num_nodes_deleted in \
                swprofile_distribution.items():
            if software_profile.lockedState == 'HardLocked':
                errors.append(
                    f'Nodes cannot be deleted from hard locked software'
                    ' profile [{software_profile.name}]'
                )

                continue

            if software_profile.minNodes and \
                    len(software_profile.nodes) - \
                    num_nodes_deleted < software_profile.minNodes:
                if force and software_profile.lockedState == 'SoftLocked':
                    # allow deletion of nodes when force is set and profile
                    # is soft locked
                    continue

                # do not allow number of software profile nodes to drop
                # below configured minimum
                errors.append(
                    'Software profile [{}] requires minimum of {} nodes;'
                    ' denied request to delete {} node(s)'.format(
                        software_profile.name, software_profile.minNodes,
                        num_nodes_deleted
                    )
                )

                continue

            if software_profile.lockedState == 'SoftLocked' and not force:
                errors.append(
                    'Nodes cannot be deleted from soft locked software'
                    f' profile [{software_profile.name}]'
                )

        if errors:
            raise OperationFailed('\n'.join(errors))

    def __delete_nodes(self, session: Session, kitmgr: KitActionsManager,
                       nodes: List[NodeModel]) -> None:
        """
        :raises DeleteNodeFailed:
        """

        hwprofile_nodes = self.__pre_delete_nodes(kitmgr, nodes)

        # commit node state changes to database
        session.commit()

        for hwprofile, node_data_dicts in hwprofile_nodes.items():
            # build list of NodeModels
            node_objs: List[NodeModel] = [
                node_data_dict['node'] for node_data_dict in node_data_dicts
            ]

            # Call resource adapter deleteNode() entry point
            self.__get_resource_adapter(
                session, hwprofile
            ).deleteNode(node_objs)

            # Perform delete node action for each node in hwprofile
            for node_data_dict in node_data_dicts:
                # get JSON object for node record
                node_dict = NodeSchema(
                    only=('hardwareprofile', 'softwareprofile', 'name',
                          'state'),
                    exclude=('softwareprofile.metadata',)
                ).dump(node_data_dict['node']).data

                # Delete the Node
                self._logger.debug('Deleting node [%s]', node_dict['name'])

                #
                # Fire node state change events
                #
                NodeStateChanged.fire(
                    node=node_dict,
                    previous_state=node_data_dict['previous_state']
                )

                self.__delete_last_tag(session, node_data_dict['node'].tags)

                session.delete(node_data_dict['node'])

                self.__post_delete(kitmgr, node_dict)

                self._logger.info('Node [%s] deleted', node_dict['name'])

            # clean up add host session cache
            self._addHostManager.delete_sessions(set([
                node.addHostSession for node in node_objs
                if node.addHostSession
            ]))

        self.__scheduleUpdate()

    def __pre_delete_nodes(self, kitmgr: KitActionsManager,
                           nodes: List[NodeModel]) \
            -> DefaultDict[HardwareProfileModel, List[NodeModel]]:
        """Collect nodes being deleted, call pre-delete kit action,
        mark them for deletion, and return dict containing nodes
        keyed by hardware profile.
        """

        hwprofile_nodes = defaultdict(list)

        #
        # Mark node states as deleted in the database
        #
        for node in nodes:
            # call pre-delete host kit action
            kitmgr.pre_delete_host(
                node.hardwareprofile.name,
                get_node_swprofile_name(node),
                nodes=[node.name]
            )

            #
            # Capture previous state and node data as a dict for firing
            # the event later on
            #
            hwprofile_nodes[node.hardwareprofile].append({
                'node': node,
                'previous_state': node.state
            })

            # mark node deleted
            node.state = state.NODE_STATE_DELETED

        return hwprofile_nodes

    def __delete_last_tag(self, session: Session,
                          tags: List[NodeTagModel]) -> None:
        """If the last node associated with the tag is deleted, delete th
        tag.
        """
        for tag in tags:
            if len(tag.nodes) == 1 and \
                    not tag.softwareprofiles and \
                    not tag.hardwareprofiles:
                self._logger.info('Deleting tag [%s]', tag.name)

                session.delete(tag)

    def __get_resource_adapter(self, session: Session,
                               hardwareProfile: HardwareProfileModel):
        """
        Raises:
            OperationFailed
        """

        if not hardwareProfile.resourceadapter:
            raise OperationFailed(
                'Hardware profile [%s] does not have an associated'
                ' resource adapter' % (hardwareProfile.name))

        adapter = resourceAdapterFactory.get_api(
            hardwareProfile.resourceadapter.name)

        adapter.session = session

        return adapter

    def __process_delete_node_result(self, nodeErrorDict):
        # REALLY!?!? Convert a list of Nodes objects into a list of
        # node names so we can report the list back to the end-user.
        # This needs to be FIXED!

        result = {}
        nodes_deleted = []

        for key, nodeList in nodeErrorDict.items():
            result[key] = [dbNode.name for dbNode in nodeList]

            if key == 'NodesDeleted':
                for node in nodeList:
                    node_deleted = {
                        'name': node.name,
                        'hardwareprofile': node.hardwareprofile.name,
                    }

                    if node.softwareprofile:
                        node_deleted['softwareprofile'] = \
                            node.softwareprofile.name

                    nodes_deleted.append(node_deleted)

        return result, nodes_deleted

    def __post_delete(self, kitmgr: KitActionsManager, node: dict):
        """Call post-delete kit action for deleted node and clean up node
        state files (ie. Puppet certificate, etc.).

        'node' is a JSON object representing the deleted node.
        """

        kitmgr.post_delete_host(
            node['hardwareprofile']['name'],
            node['softwareprofile']['name']
            if node['softwareprofile'] else None,
            nodes=[node['name']]
        )

        # remove Puppet cert, etc.
        self.__cleanup_node_state_files(node)

    def __cleanup_node_state_files(self, node_dict: dict):
        # Remove the Puppet cert
        self._bhm.deletePuppetNodeCert(node_dict['name'])

        self._bhm.nodeCleanup(node_dict['name'])

    def __scheduleUpdate(self):
        self._syncApi.scheduleClusterUpdate()

    def getInstallerNode(self, session,
                         optionDict: Optional[OptionDict] = None):
        return self._nodeDbApi.getNode(
            session,
            self._cm.getInstaller(),
            optionDict=get_default_relations(optionDict))

    def getProvisioningInfo(self, session: Session, nodeName):
        return self._nodeDbApi.getProvisioningInfo(session, nodeName)

    def startupNode(self, session, nodespec: str,
                    remainingNodeList: List[NodeModel] = None,
                    bootMethod: str = 'n') -> None:
        """
        Raises:
            NodeNotFound
        """

        try:
            nodes = self._nodesDbHandler.expand_nodespec(session, nodespec)

            if not nodes:
                raise NodeNotFound(
                    'No matching nodes for nodespec [%s]' % (nodespec))

            # Break list of nodes into dict keyed on hardware profile
            nodes_dict = self.__processNodeList(nodes)

            for dbHardwareProfile, detailsDict in nodes_dict.items():
                # Get the ResourceAdapter
                adapter = self.__getResourceAdapter(dbHardwareProfile)

                # Call startup action extension
                adapter.startupNode(
                    detailsDict['nodes'],
                    remainingNodeList=remainingNodeList or [],
                    tmpBootMethod=bootMethod)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def shutdownNode(self, session, nodespec: str,
                     bSoftShutdown: bool = False) -> None:
        """
        Raises:
            NodeNotFound
        """

        try:
            nodes = self._nodesDbHandler.expand_nodespec(session, nodespec)

            if not nodes:
                raise NodeNotFound(
                    'No matching nodes for nodespec [%s]' % (nodespec))

            d = self.__processNodeList(nodes)

            for dbHardwareProfile, detailsDict in d.items():
                # Get the ResourceAdapter
                adapter = self.__getResourceAdapter(dbHardwareProfile)

                # Call shutdown action extension
                adapter.shutdownNode(detailsDict['nodes'], bSoftShutdown)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self._logger.exception(str(ex))
            raise

    def rebootNode(self, session, nodespec: str, bSoftReset: bool = False,
                   bReinstall: bool = False) -> None:
        """
        Raises:
            NodeNotFound
        """

        nodes = self._nodesDbHandler.expand_nodespec(session, nodespec)
        if not nodes:
            raise NodeNotFound(
                'No nodes matching nodespec [%s]' % (nodespec))

        if bReinstall:
            for dbNode in nodes:
                self._bhm.setNodeForNetworkBoot(session, dbNode)

        for dbHardwareProfile, detailsDict in \
                self.__processNodeList(nodes).items():
            # iterate over hardware profile/nodes dict to reboot each
            # node
            adapter = self.__getResourceAdapter(dbHardwareProfile)

            # Call reboot action extension
            adapter.rebootNode(detailsDict['nodes'], bSoftReset)

        session.commit()

    def getNodesByNodeState(self, session, node_state: str,
                            optionDict: Optional[OptionDict] = None) \
            -> TortugaObjectList:
        """
        Get nodes by state
        """

        return self.__populate_nodes(
            session,
            self._nodeDbApi.getNodesByNodeState(
                session, node_state,
                optionDict=get_default_relations(optionDict)))

    def getNodesByNameFilter(self, session, nodespec: str,
                             optionDict: OptionDict = None,
                             include_installer: Optional[bool] = True) \
            -> TortugaObjectList:
        """
        Return TortugaObjectList of Node objects matching nodespec
        """

        return self.__populate_nodes(
            session,
            self._nodeDbApi.getNodesByNameFilter(
                session,
                nodespec,
                optionDict=get_default_relations(optionDict),
                include_installer=include_installer
            )
        )

    def getNodesByAddHostSession(self, session, addHostSession: str,
                                 optionDict: OptionDict = None) \
            -> TortugaObjectList:
        """
        Return TortugaObjectList of Node objects matching add host session
        """

        return self.__populate_nodes(
            session,
            self._nodeDbApi.getNodesByAddHostSession(
                session,
                addHostSession,
                optionDict=get_default_relations(optionDict)))

    def __processNodeList(self, dbNodes: List[NodeModel]) \
            -> Dict[HardwareProfileModel, Dict[str, list]]:
        """
        Returns dict indexed by hardware profile, each with a list of
        nodes in the hardware profile
        """

        d: Dict[HardwareProfileModel, Dict[str, list]] = {}

        for dbNode in dbNodes:
            if dbNode.hardwareprofile not in d:
                d[dbNode.hardwareprofile] = {
                    'nodes': [],
                }

            d[dbNode.hardwareprofile]['nodes'].append(dbNode)

        return d

    def __getResourceAdapter(self, hardwareProfile: HardwareProfileModel):
        """
        Raises:
            OperationFailed
        """

        if not hardwareProfile.resourceadapter:
            raise OperationFailed(
                'Hardware profile [%s] does not have an associated'
                ' resource adapter' % (hardwareProfile.name))

        return resourceAdapterFactory.get_api(
            hardwareProfile.resourceadapter.name) \
            if hardwareProfile.resourceadapter else None


def get_default_relations(relations: Optional[OptionDict]):
    """
    Ensure hardware and software profiles and tags are populated when
    serializing node records.
    """

    result = relations.copy() if relations else {}

    # ensure software and hardware profile relations are loaded
    result.update({
        'hardwareprofile': True,
        'softwareprofile': True,
        'tags': True,
        'instance': True,
    })

    return result


def init_async_node_request(action: str, data: Any, *,
                            admin_id: Optional[int] = None):
    """
    Serialize async node request to NodeRequest (db) object
    """

    request = NodeRequest(
        request=json.dumps(data),
        timestamp=datetime.datetime.utcnow(),
        action=action,
        addHostSession=AddHostManager().createNewSession(),
        admin_id=admin_id,
    )

    return request


def get_node_swprofile_name(node: NodeModel) -> Optional[str]:
    return node.softwareprofile.name if node.softwareprofile else None
