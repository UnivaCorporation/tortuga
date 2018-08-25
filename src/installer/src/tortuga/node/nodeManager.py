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

import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm.session import Session
from tortuga.addhost.addHostManager import AddHostManager
from tortuga.addhost.addHostServerLocal import AddHostServerLocal
from tortuga.config.configManager import ConfigManager
from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.db.models.hardwareProfile import \
    HardwareProfile as HardwareProfileModel
from tortuga.db.models.node import Node as NodeModel
from tortuga.db.models.softwareProfile import \
    SoftwareProfile as SoftwareProfileModel
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.events.types import NodeStateChanged
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.nodeSoftwareProfileLocked import \
    NodeSoftwareProfileLocked
from tortuga.exceptions.nodeTransferNotValid import NodeTransferNotValid
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.exceptions.profileMappingNotAllowed import \
    ProfileMappingNotAllowed
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.exceptions.volumeDoesNotExist import VolumeDoesNotExist
from tortuga.kit.actions import KitActionsManager
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.san import san
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
        self._hardwareProfileDbApi = HardwareProfileDbApi()
        self._cm = ConfigManager()
        self._san = san.San()
        self._bhm = osUtility.getOsObjectFactory().getOsBootHostManager(
            self._cm)
        self._syncApi = SyncApi()
        self._nodesDbHandler = NodesDbHandler()

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

        self.getLogger().debug(
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

        # Set software profile of new node; if the software profile is None,
        # attempt to set the software profile to the idle software profile
        # of the associated hardware profile. This may also be None, in
        # which case the software profile is undefined.
        node.softwareprofile = dbSoftwareProfile \
            if dbSoftwareProfile else dbHardwareProfile.idlesoftwareprofile

        node.isIdle = dbSoftwareProfile.isIdle \
            if dbSoftwareProfile else True

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
                    optionDict: OptionDict = None,
                    deleting: bool = False) \
            -> List[Node]:
        """
        Return all nodes

        """
        return self.__populate_nodes(
            session,
            self._nodeDbApi.getNodeList(
                session,
                tags=tags,
                optionDict=get_default_relations(optionDict),
                deleting=deleting
            )
        )

    def __populate_nodes(self, session: Session, nodes: List[Node]) -> List[Node]:
        """
        Expand non-database fields in Node objects

        """
        swprofile_map: Dict[str, Any] = {}

        # dict keyed on resource adapter name, value is resource adapter class
        adapter_map: Dict[str, Any] = {}

        for node in nodes:
            adapter_name = \
                node.getHardwareProfile().getResourceAdapter().getName() \
                if node.getHardwareProfile().getResourceAdapter() else \
                'default'

            ResourceAdapterClass = adapter_map.get(adapter_name)
            if ResourceAdapterClass is None:
                # Query vcpus from resource adapter
                ResourceAdapterClass = \
                    resourceAdapterFactory.get_resourceadapter_class(
                        adapter_name)

                adapter_map[adapter_name] = ResourceAdapterClass

            adapter = ResourceAdapterClass()
            adapter.session = session

            # Update Node object
            node.setVcpus(adapter.get_node_vcpus(node.getName()))

            if not node.getSoftwareProfile():
                continue

            swprofile_name = node.getSoftwareProfile().getName()

            metadata = swprofile_map.get(swprofile_name)
            if metadata is None:
                metadata = \
                    SoftwareProfileManager().get_software_profile_metadata(
                        session, node.getSoftwareProfile().getName())

                swprofile_map[swprofile_name] = metadata

            node.getSoftwareProfile().setMetadata(metadata)

        return nodes

    def updateNode(self, session, nodeName, updateNodeRequest):
        """
        Calls updateNode() method of resource adapter
        """

        self.getLogger().debug('updateNode(): name=[{0}]'.format(nodeName))

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
                self.getLogger().debug(
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

        self.getLogger().debug(
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

            self.getLogger().info(msg)
        else:
            self.getLogger().info(
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

    def __process_nodeErrorDict(self, nodeErrorDict):
        result = {}
        nodes_deleted = []

        for key, nodeList in nodeErrorDict.items():
            result[key] = [dbNode.name for dbNode in nodeList]

            if key == 'NodesDeleted':
                for node in nodeList:
                    node_deleted = {
                        'name': node.name,
                        'hardwareprofile': node.hardwareprofile.name,
                        'addHostSession': node.addHostSession,
                    }

                    if node.softwareprofile:
                        node_deleted['softwareprofile'] = \
                            node.softwareprofile.name

                    nodes_deleted.append(node_deleted)

        return result, nodes_deleted

    def deleteNode(self, session, nodespec: str, force: bool = False):
        """
        Delete node by nodespec

        Raises:
            NodeNotFound
        """

        kitmgr = KitActionsManager()
        kitmgr.session = session

        try:
            nodes = self._nodesDbHandler.expand_nodespec(
                session, nodespec, include_installer=False)
            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            self.__validate_delete_nodes_request(nodes, force)

            self.__preDeleteHost(kitmgr, nodes)

            nodeErrorDict = self.__delete_node(session, nodes)

            # REALLY!?!? Convert a list of Nodes objects into a list of
            # node names so we can report the list back to the end-user.
            # This needs to be FIXED!

            result, nodes_deleted = self.__process_nodeErrorDict(nodeErrorDict)

            session.commit()

            # ============================================================
            # Perform actions *after* node deletion(s) have been committed
            # to database.
            # ============================================================

            self.__postDeleteHost(kitmgr, nodes_deleted)

            addHostSessions = set(
                [tmpnode['addHostSession'] for tmpnode in nodes_deleted]
            )

            if addHostSessions:
                AddHostManager().delete_sessions(addHostSessions)

            for nodeName in result['NodesDeleted']:
                # Remove the Puppet cert
                self._bhm.deletePuppetNodeCert(nodeName)

                self._bhm.nodeCleanup(nodeName)

                self.getLogger().info('Node [%s] deleted' % (nodeName))

            # Schedule a cluster update
            self.__scheduleUpdate()

            return result
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
                    len(software_profile.nodes) - num_nodes_deleted < \
                        software_profile.minNodes:
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

    def __delete_node(self, session: Session, dbNodes: List[NodeModel]) \
            -> Dict[str, List[NodeModel]]:
        """
        Raises:
            DeleteNodeFailed
        """

        result: Dict[str, list] = {
            'NodesDeleted': [],
            'DeleteNodeFailed': [],
            'SoftwareProfileLocked': [],
            'SoftwareProfileHardLocked': [],
        }

        nodes: Dict[HardwareProfileModel, List[NodeModel]] = {}
        events_to_fire: List[dict] = []

        #
        # Mark node states as deleted in the database
        #
        for dbNode in dbNodes:
            #
            # Capture previous state and node data as a dict for firing
            # the event later on
            #
            event_data = {
                'previous_state': dbNode.state,
                'node': Node.getFromDbDict(dbNode.__dict__).getCleanDict()
            }

            dbNode.state = state.NODE_STATE_DELETED
            event_data['node']['state'] = 'Deleted'

            if dbNode.hardwareprofile not in nodes:
                nodes[dbNode.hardwareprofile] = [dbNode]
            else:
                nodes[dbNode.hardwareprofile].append(dbNode)

        session.commit()

        #
        # Fire node state change events
        #
        for event in events_to_fire:
            NodeStateChanged.fire(node=event['node'],
                                  previous_state=event['previous_state'])

        #
        # Call resource adapter with batch(es) of node lists keyed on
        # hardware profile.
        #
        for hwprofile, hwprofile_nodes in nodes.items():
            # Get the ResourceAdapter
            adapter = self.__get_resource_adapter(hwprofile)
            adapter.session = session

            # Call the resource adapter
            adapter.deleteNode(hwprofile_nodes)

            # Iterate over all nodes in hardware profile, completing the
            # delete operation.
            for dbNode in hwprofile_nodes:
                # Remove PXE boot file and remove lease from dhcp server
                if hwprofile.location == 'local':
                    # Only attempt to remove local boot configuration for
                    # nodes that are marked as 'local'

                    self._bhm.rmPXEFile(dbNode)
                    self._bhm.removeDhcpLease(dbNode)

                for tag in dbNode.tags:
                    if len(tag.nodes) == 1 and \
                            not tag.softwareprofiles and \
                            not tag.hardwareprofiles:
                        session.delete(tag)

                # Delete the Node
                self.getLogger().debug('Deleting node [%s]' % (dbNode.name))

                session.delete(dbNode)

                result['NodesDeleted'].append(dbNode)

        return result

    def __get_resource_adapter(self, hardwareProfile):
        """
        Raises:
            OperationFailed
        """

        if not hardwareProfile.resourceadapter:
            raise OperationFailed(
                'Hardware profile [%s] does not have an associated'
                ' resource adapter' % (hardwareProfile.name))

        return resourceAdapterFactory.get_api(
            hardwareProfile.resourceadapter.name)

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

    def __preDeleteHost(self, kitmgr: KitActionsManager, nodes):
        self.getLogger().debug(
            '__preDeleteHost(): nodes=[%s]' % (
                ' '.join([node.name for node in nodes])))

        for node in nodes:
            kitmgr.pre_delete_host(
                node.hardwareprofile.name,
                node.softwareprofile.name if node.softwareprofile else None,
                nodes=[node.name])

    def __postDeleteHost(self, kitmgr, nodes_deleted):
        # 'nodes_deleted' is a list of dicts of the following format:
        #
        # {
        #     'name': 'compute-01',
        #     'softwareprofile': 'Compute',
        #     'hardwareprofile': 'LocalIron',
        # }
        #
        # if the node does not have an associated software profile, the
        # dict does not contain the key 'softwareprofile'.

        self.getLogger().debug(
            '__postDeleteHost(): nodes_deleted=[%s]' % (nodes_deleted))

        if not nodes_deleted:
            self.getLogger().debug('No nodes deleted in this operation')

            return

        for node_dict in nodes_deleted:
            kitmgr.post_delete_host(
                node_dict['hardwareprofile'],
                node_dict['softwareprofile']
                if 'softwareprofile' in node_dict else None,
                nodes=[node_dict['name']])

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

    def __group_by_hwprofile(self, results: List[Dict[str, Any]]) \
            -> Dict[HardwareProfileModel, List[Dict[str, Any]]]:
        # group nodes by hardware profile
        result: Dict[HardwareProfileModel, List[Dict[str, Any]]] = {}

        for transferResultDict in results:
            hardware_profile = transferResultDict['node'].hardwareprofile

            if hardware_profile not in result:
                result[hardware_profile] = []

            result[hardware_profile].append(transferResultDict)

        return result

    def __process_transfer_requests(
            self,
            session: Session,
            hwProfileMap: Dict[HardwareProfileModel, List[Dict[str, Any]]],
            dst_swprofile: SoftwareProfileModel) \
                -> Dict[str, Dict[str, List[NodeModel]]]:
        """

        """

        res: Dict[str, Dict[str, List[NodeModel]]] = {}

        # Kill two birds with one stone... do the resource adapter
        # action as well as populate the nodeTransferDict. This saves
        # having to iterate twice on the same result data.
        for hwprofile, nodesDict in hwProfileMap.items():
            node_tuples: List[Tuple[NodeModel, SoftwareProfileModel]] = []

            for node, src_swprofile in \
                    [(nodeDict['node'], nodeDict['prev_softwareprofile'])
                     for nodeDict in nodesDict]:
                if src_swprofile.name not in res:
                    res[src_swprofile.name] = {
                        'added': [],
                        'removed': [node],
                    }
                else:
                    res[src_swprofile.name]['removed'].append(node)

                if dst_swprofile.name not in res:
                    res[dst_swprofile.name] = {
                        'added': [node],
                        'removed': [],
                    }
                else:
                    res[dst_swprofile.name]['added'].append(node)

                # The destination software profile is available through
                # node relationship.
                node_tuples.append((node, src_swprofile))

            # get resource adapter for hardware profile
            adapter = self.__get_resource_adapter(hwprofile)

            # call resource adapter
            adapter.transferNode(node_tuples, dst_swprofile)

            session.commit()

        return res

    def __transferNodeCommon(self, session: Session,
                             dbDstSoftwareProfile: SoftwareProfileModel,
                             results: List[Dict[str, Any]]):
        transfer_dict = self.__process_transfer_requests(
            session,
            self.__group_by_hwprofile(results),
            dbDstSoftwareProfile
        )

        # Now call the 'refresh' action to all participatory components
        kitmgr = KitActionsManager()
        kitmgr.session = session

        kitmgr.refresh(transfer_dict)

        return results

    def transferNode(self, session, nodespec: str,
                     dstSoftwareProfileName: str, bForce: bool = False):
        """
        Transfer nodes defined by 'nodespec' to 'dstSoftwareProfile'

        Raises:
            NodeNotFound
            SoftwareProfileNotFound
            NodeTransferNotValid
        """

        nodes: List[NodeModel] = self._nodesDbHandler.expand_nodespec(
            session, nodespec)

        if not nodes:
            raise NodeNotFound(
                'No nodes matching nodespec [%s]' % (nodespec))

        dbDstSoftwareProfile = \
            SoftwareProfilesDbHandler().getSoftwareProfile(
                session, dstSoftwareProfileName)

        results: List[Dict[str, Any]] = []

        for node in nodes:
            if node.hardwareprofile not in\
                    dbDstSoftwareProfile.hardwareprofiles:
                raise ProfileMappingNotAllowed(
                    'Node [%s] belongs to hardware profile [%s] which is'
                    ' not allowed to use software profile [%s]' % (
                        node.name, node.hardwareprofile.name,
                        dbDstSoftwareProfile.name))

            # Check to see if the node is already using the requested
            # software profile
            if not bForce and not self.__isNodeStateInstalled(node):
                raise NodeTransferNotValid(
                    'Node [{}] in state [{}] cannot be'
                    ' transferred'.format(node.name, node.state))

            # Check to see if the node is already using the requested
            # software profile
            if node.softwareprofile == dbDstSoftwareProfile:
                msg = 'Node [%s] is already in software profile [%s]' % (
                    node.name, dbDstSoftwareProfile.name)

                self.getLogger().info(msg)

                raise NodeTransferNotValid(msg)

            self.getLogger().debug(
                'transferNode: Transferring node [%s] to'
                ' software profile [%s]' % (
                    node.name, dbDstSoftwareProfile.name))

            # Check to see if the node is locked
            if self.__isNodeLocked(node):
                raise NodeSoftwareProfileLocked(
                    "Node [%s] can't be transferred while locked" % (
                        node.name))

            result: Dict[str, Any] = {
                'prev_softwareprofile': node.softwareprofile,
                'node': node,
            }

            node.softwareprofile = dbDstSoftwareProfile

            results.append(result)

        return self.__transferNodeCommon(
            session, dbDstSoftwareProfile, results)

    def transferNodes(self, session, srcSoftwareProfileName: str,
                      dstSoftwareProfileName: str,
                      count: int, bForce: bool = False): \
            # pylint: disable=unused-argument
        """
        Transfer 'count' nodes from 'srcSoftwareProfile' to
        'dstSoftwareProfile'

        Raises:
            SoftwareProfileNotFound
            NodeTransferNotValid
        """

        # It is not necessary to specify a source software profile. If
        # not specified, pick any eligible nodes in the hardware profile
        # mapped to the destination software profile. Don't ask me who
        # uses this capability, but it's here if you need it...

        dbSrcSoftwareProfile = SoftwareProfilesDbHandler().\
            getSoftwareProfile(
                session, srcSoftwareProfileName) \
            if srcSoftwareProfileName else None

        dbDstSoftwareProfile = SoftwareProfilesDbHandler().\
            getSoftwareProfile(session, dstSoftwareProfileName)

        # First sanity check... ensure there is actually something to do.
        if dbSrcSoftwareProfile == dbDstSoftwareProfile:
            raise NodeTransferNotValid(
                'Source and destination software profiles are the same')

        # Get list of Unlocked nodes
        dbUnlockedNodeList = self.__getTransferrableNodes(
            dbSrcSoftwareProfile, dbDstSoftwareProfile)

        # If the source software profile is specified, only use nodes from
        # it, otherwise get list of nodes for compatible hardware profile.

        nUnlockedNodes = len(dbUnlockedNodeList)

        if nUnlockedNodes < count:
            # Not enough nodes available, include SoftLocked nodes as well.

            dbSoftLockedNodes = self.__getSoftLockedNodes(
                dbSrcSoftwareProfile, dbDstSoftwareProfile)

            nSoftLockedNodes = len(dbSoftLockedNodes)

            if nSoftLockedNodes == 0:
                self.getLogger().debug(
                    '[%s] No softlocked nodes available' % (
                        self.__module__))

            nNodesAvailable = nUnlockedNodes + nSoftLockedNodes

            if nNodesAvailable == 0:
                # Use a different error message to be friendly...
                msg = 'No nodes available to transfer'

                self.getLogger().error(msg)

                raise NodeTransferNotValid(msg)

            if nNodesAvailable < count:
                # We still do not have enough nodes to transfer.
                msg = ('Insufficient nodes available to transfer;'
                        ' %d available, %d requested' % (
                            nNodesAvailable, count))

                self.getLogger().info(msg)

                raise NodeTransferNotValid(msg)

            nRequiredNodes = count - nUnlockedNodes

            dbNodeList = dbUnlockedNodeList + \
                dbSoftLockedNodes[:nRequiredNodes]
        else:
            dbNodeList = dbUnlockedNodeList[:count]

        results = self.transferNode(
            session, dbNodeList, dbDstSoftwareProfile)

        return self.__transferNodeCommon(
            session, dbDstSoftwareProfile, results)

    def idleNode(self, session, nodespec):
        """
        Raises:
            NodeNotFound
            NodeAlreadyIdle
            NodeSoftwareProfileLocked
        """

        try:
            nodes = self._nodesDbHandler.expand_nodespec(session, nodespec)

            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            idleSoftwareProfilesDict = {}
            d = {}

            results = {
                'NodeAlreadyIdle': [],
                'NodeSoftwareProfileLocked': [],
                'success': [],
            }

            # Iterate over all nodes in the node spec, idling each one
            for dbNode in nodes:
                # Check to see if the node is already idle
                if dbNode.isIdle:
                    results['NodeAlreadyIdle'].append(dbNode)

                    continue

                hardware_profile = dbNode.hardwareprofile

                # Get the software profile
                # dbSoftwareProfile = dbNode.softwareprofile

                # Check to see if the node is locked
                if self.__isNodeLocked(dbNode):
                    results['NodeSoftwareProfileLocked'].append(dbNode)

                    continue

                if hardware_profile.name not in d:
                    # Get the ResourceAdapter
                    adapter = self.__getResourceAdapter(hardware_profile)

                    d[hardware_profile.name] = {
                        'adapter': adapter,
                        'nodes': [],
                    }
                else:
                    adapter = d[hardware_profile.name]['adapter']

                # Call suspend action extension
                if adapter.suspendActiveNode(dbNode):
                    # Change node status in the DB
                    dbNode.isIdle = True

                    continue

                # If we could not suspend the node, shut it down
                if dbNode.softwareprofile.name not in idleSoftwareProfilesDict:
                    idleSoftwareProfilesDict[dbNode.softwareprofile.name] = {
                        'idled': [],
                        'added': [],
                    }

                idleSoftwareProfilesDict[dbNode.softwareprofile.name]['idled'].append(dbNode)

                # Idle the Node
                if hardware_profile.idlesoftwareprofile:
                    self.getLogger().debug(
                        'Idling node [%s] to idle software profile [%s]' % (
                            dbNode.name,
                            hardware_profile.idlesoftwareprofile.name))

                    idle_profile_name = \
                        hardware_profile.idlesoftwareprofile.name

                    # If the idle software profile is defined, include it in
                    # the refresh information for this node.
                    if idle_profile_name not in idleSoftwareProfilesDict:
                        idleSoftwareProfilesDict[idle_profile_name] = {
                            'idled': [],
                            'added': [],
                        }

                    idleSoftwareProfilesDict[
                        hardware_profile.idlesoftwareprofile.name][
                            'added'].append(dbNode)

                dbNode.softwareprofile = hardware_profile.idlesoftwareprofile

                # The idle status has to go with this commit or we are
                # inconsistent...
                dbNode.isIdle = True

                # session.commit()

                # TODO: fix this at some point. Basically, it is a list of
                # nodes that have been successfully idled.
                d[hardware_profile.name]['nodes'].append(dbNode)

            events_to_fire = []

            # Call idle action extension
            for nodeDetails in d.values():
                # Call resource adapter
                nodeState = nodeDetails['adapter'].\
                    idleActiveNode(nodeDetails['nodes'])

                # Node state is consistent for all nodes within the same
                # hardware profile.
                for dbNode in nodeDetails['nodes']:
                    event_data = None
                    #
                    # If the node state is changing, then we need to be
                    # prepared to fire an event after the data has been
                    #  persisted.
                    #
                    if dbNode.state != nodeState:
                        event_data = {'previous_state': dbNode.state}

                    dbNode.state = nodeState

                    #
                    # Serialize the node for the event, if required
                    #
                    if event_data:
                        event_data['node'] = Node.getFromDbDict(
                            dbNode.__dict__).getCleanDict()
                        events_to_fire.append(event_data)

                # Add idled node to 'success' list
                results['success'].extend(nodeDetails['nodes'])

            session.commit()

            #
            # Fire node state change events
            #
            for event in events_to_fire:
                NodeStateChanged.fire(node=event['node'],
                                      previous_state=event['previous_state'])

            # Convert list of Nodes to list of node names for providing
            # user feedback.

            result_dict = {}
            for key, dbNodes in results.items():
                result_dict[key] = [dbNode.name for dbNode in dbNodes]

            session.commit()

            # Remove Puppet certificate(s) for idled node(s)
            for node_name in result_dict['success']:
                # Remove Puppet certificate for idled node
                self._bhm.deletePuppetNodeCert(node_name)

            # Schedule a cluster update
            self.__scheduleUpdate()

            return result_dict
        except Exception:
            session.rollback()

            raise

    def __process_activateNode_results(self, tmp_results, dstswprofilename):
        results = {}

        for key, values in tmp_results.items():
            # With the exception of the "ProfileMappingNotAllowed" dict
            # item, all items in the dict are lists of nodes.
            if key != 'ProfileMappingNotAllowed':
                results[key] = [dbNode.name for dbNode in values]
            else:
                results[key] = \
                    [(value[0].name, value[1], value[2])
                     for value in values]

        if tmp_results['success']:
            # Iterate over activated nodes, creating dict keyed on
            # 'addHostSession'
            addHostSessions = {}

            for node in tmp_results['success']:
                if node.addHostSession not in addHostSessions:
                    addHostSessions[node.addHostSession] = []

                addHostSessions[node.addHostSession] = \
                    node.hardwareprofile.name

            # For each 'addHostSession', call postAddHost()
            for addHostSession, hwprofile in addHostSessions.items():
                AddHostManager().postAddHost(
                    hwprofile, dstswprofilename, addHostSession)

        return results

    def activateNode(self, session, nodespec: str, softwareProfileName: str):
        """
        Raises:
            SoftwareProfileNotFound
            NodeNotFound
            TortugaException
        """

        try:
            dbDstSoftwareProfile = \
                SoftwareProfilesDbHandler().getSoftwareProfile(
                    session, softwareProfileName) \
                if softwareProfileName else None

            dbNodes = self._nodesDbHandler.expand_nodespec(session, nodespec)

            if not dbNodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            d: Dict[str, Any] = {}

            activateNodeResults: Dict[str, list] = {
                'NodeAlreadyActive': [],
                'SoftwareProfileNotFound': [],
                'InvalidArgument': [],
                'NodeSoftwareProfileLocked': [],
                'ProfileMappingNotAllowed': [],
                'success': [],
            }

            activateSoftwareProfilesDict = {}

            for dbNode in dbNodes:
                self.getLogger().debug(
                    'Attempting to activate node [%s]' % (dbNode.name))

                # Check to see if the node is already active
                if not dbNode.isIdle:
                    # Attempting to activate an "active" node
                    activateNodeResults['NodeAlreadyActive'].append(dbNode)

                    continue

                # Flag to indicate if the node has been activated to a software
                # profile that differs from the software profile that it was
                # previously in
                softwareProfileChanged = False

                # If the node is only suspended and has a software profile, no
                # need to force the user to tell us what the software profile
                # is.
                if not dbDstSoftwareProfile:
                    if not dbNode.softwareprofile:
                        # We don't know what to do with the specified node.
                        # Destination software profile not specified and node
                        # does not have an associated software profile.

                        activateNodeResults['SoftwareProfileNotFound'].append(
                            dbNode)

                        continue

                    dbSoftwareProfile = dbNode.softwareprofile
                else:
                    softwareProfileChanged = \
                        dbNode.softwareprofile is None or \
                        dbNode.softwareprofile != dbDstSoftwareProfile

                    dbSoftwareProfile = dbNode.softwareprofile \
                        if not softwareProfileChanged else dbDstSoftwareProfile

                if dbSoftwareProfile and dbSoftwareProfile.isIdle:
                    # Attempt to activate node into an idle software profile
                    activateNodeResults['InvalidArgument'].append(dbNode)

                    continue

                # Check to see if the node is locked
                if self.__isNodeLocked(dbNode):
                    # Locked nodes cannot be activated
                    activateNodeResults['NodeSoftwareProfileLocked'].append(
                        dbNode)

                    continue

                if dbSoftwareProfile and \
                        dbNode.hardwareprofile not in dbSoftwareProfile.\
                        hardwareprofiles:
                    # This result list is a tuple of (node, hardwareprofile
                    # name, software profile name) for reporting the error back
                    # to the caller.
                    activateNodeResults['ProfileMappingNotAllowed'].\
                        append((dbNode,
                                dbNode.hardwareprofile.name,
                                dbSoftwareProfile.name,))

                    continue

                # Activate the Node
                self.getLogger().debug(
                    'Activating node [%s] to software profile [%s]' % (
                        dbNode.name, dbSoftwareProfile.name))

                if dbNode.softwareprofile:
                    activateSoftwareProfilesDict[dbNode.softwareprofile.name] = {
                        'removed': [dbNode],
                    }

                if softwareProfileChanged and dbSoftwareProfile.name:
                    activateSoftwareProfilesDict[dbSoftwareProfile.name] = {
                        'activated': [dbNode],
                    }

                dbNode.softwareprofile = dbSoftwareProfile

                session.commit()

                if dbNode.hardwareprofile.name not in d:
                    # Get the ResourceAdapter
                    adapter = self.__getResourceAdapter(dbNode.hardwareprofile)

                    d[dbNode.hardwareprofile.name] = {
                        'adapter': adapter,
                        'nodes': [],
                    }

                d[dbNode.hardwareprofile.name]['nodes'].append(
                    (dbNode, dbSoftwareProfile.name, softwareProfileChanged))

            # 'd' dict is indexed by hardware profile
            for nodesDetail in d.values():
                # Iterate over all idled nodes
                for dbNode, softwareProfileName_, bSoftwareProfileChanged in \
                        nodesDetail['nodes']:
                    nodesDetail['adapter'].activateIdleNode(
                        dbNode, softwareProfileName_,
                        bSoftwareProfileChanged)

                    dbNode.isIdle = False

                    activateNodeResults['success'].append(dbNode)

            session.commit()

            results = self.__process_activateNode_results(
                activateNodeResults, softwareProfileName)

            session.commit()

            # Schedule a cluster update
            self.__scheduleUpdate()

            return results
        except Exception:
            session.rollback()

            raise

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
            self.getLogger().exception('%s' % ex)
            raise

    def shutdownNode(self, session, nodespec: str, bSoftShutdown: bool = False) \
            -> None:
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
            self.getLogger().exception('%s' % ex)
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

    def addStorageVolume(self, nodeName: str, volume: str,
                         isDirect: Optional[str] = "DEFAULT") -> None:
        """
        Raises:
            VolumeDoesNotExist
            UnsupportedOperation
        """

        node = self.getNode(nodeName, {'hardwareprofile': True})

        # Only allow persistent volumes to be attached...
        vol = self._san.getVolume(volume)
        if vol is None:
            raise VolumeDoesNotExist('Volume [%s] does not exist' % (volume))

        if not vol.getPersistent():
            raise UnsupportedOperation(
                'Only persistent volumes can be attached')

        api = resourceAdapterFactory.get_api(
            node.getHardwareProfile().getResourceAdapter().getName())

        if isDirect == "DEFAULT":
            api.addVolumeToNode(node, volume)

        api.addVolumeToNode(node, volume, isDirect)

    def removeStorageVolume(self, nodeName: str, volume: str) -> None:
        """
        Raises:
            VolumeDoesNotExist
            UnsupportedOperation
        """

        node = self.getNode(nodeName, {'hardwareprofile': True})

        api = resourceAdapterFactory.get_api(
            node.getHardwareProfile().getResourceAdapter().getName())

        vol = self._san.getVolume(volume)

        if vol is None:
            raise VolumeDoesNotExist(
                'The volume [%s] does not exist' % (volume))

        if not vol.getPersistent():
            raise UnsupportedOperation(
                'Only persistent volumes can be detached')

        api.removeVolumeFromNode(node, volume)

    def getStorageVolumes(self, session: Session, nodeName: str):
        return self._san.getNodeVolumes(
            self.getNode(session, nodeName).getName())

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

    def __isNodeTransferrable(self, dbNode: NodeModel) -> bool:
        # Only nodes that are not locked and in Installed state are
        # eligible for transfer.
        return not self.__isNodeLocked(dbNode) and \
            self.__isNodeStateInstalled(dbNode)

    def __getNodeTransferCandidates(
            self, dbSrcSoftwareProfile: SoftwareProfileModel,
            dbDstSoftwareProfile: SoftwareProfileModel, compare_func):
        """
        Helper method for determining which nodes should be considered for
        transfer.
        """

        if dbSrcSoftwareProfile:
            # Find all nodes within this software profile that are in the
            # same hardware profile as the destination software profile.
            # Exclude all nodes that are HardLocked or not in "Installed"
            # state.
            return [
                dbNode for dbNode in dbSrcSoftwareProfile.nodes
                if dbNode.hardwareprofile in
                dbDstSoftwareProfile.hardwareprofiles and
                compare_func(dbNode)]

        # Find all nodes that are in the same hardware profile(s) as
        # the destination software profile. Exclude all nodes that are
        # HardLocked or not in "Installed" state.
        return [
            dbNode for dbHardwareProfile in
            dbDstSoftwareProfile.hardwareprofiles
            for dbNode in dbHardwareProfile.nodes
            if dbNode.softwareprofile != dbDstSoftwareProfile and
            compare_func(dbNode)]

    def __getTransferrableNodes(
            self, dbSrcSoftwareProfile: SoftwareProfileModel,
            dbDstSoftwareProfile: SoftwareProfileModel) -> List[Node]:
        """
        Return list of Unlocked nodes
        """

        return self.__getNodeTransferCandidates(
            dbSrcSoftwareProfile, dbDstSoftwareProfile,
            self.__isNodeTransferrable)

    def __getSoftLockedNodes(
            self, dbSrcSoftwareProfile: SoftwareProfileModel,
            dbDstSoftwareProfile: SoftwareProfileModel) -> List[Node]:
        """
        Return list of SoftLocked nodes
        """

        return self.__getNodeTransferCandidates(
            dbSrcSoftwareProfile, dbDstSoftwareProfile,
            self.__isNodeSoftLocked)

    def __isNodeLocked(self, dbNode: NodeModel) -> bool:
        return dbNode.lockedState != 'Unlocked'

    def __isNodeHardLocked(self, dbNode: NodeModel) -> bool:
        return dbNode.lockedState == 'HardLocked'

    def __isNodeSoftLocked(self, dbNode: NodeModel) -> bool:
        return dbNode.lockedState == 'SoftLocked'

    def __getNodeState(self, dbNode: NodeModel) -> str:
        return dbNode.state

    def __isNodeStateDeleted(self, node: NodeModel) -> bool:
        return self.__getNodeState(node) == state.NODE_STATE_DELETED

    def __isNodeStateInstalled(self, dbNode: NodeModel) -> bool:
        return self.__getNodeState(dbNode) == \
            state.NODE_STATE_INSTALLED


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
