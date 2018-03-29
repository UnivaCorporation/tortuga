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

import os
import socket
import time
from typing import NoReturn, Optional

from sqlalchemy.orm.session import Session

from tortuga.addhost.addHostManager import AddHostManager
from tortuga.addhost.addHostServerLocal import AddHostServerLocal
from tortuga.config.configManager import ConfigManager
from tortuga.db.dbManager import DbManager
from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.exceptions.volumeDoesNotExist import VolumeDoesNotExist
from tortuga.kit.actions import KitActionsManager
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility, tortugaSubprocess
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.san import san
from tortuga.db.models.node import Node as NodeModel
from tortuga.schema import NodeSchema


class NodeManager(TortugaObjectManager): \
        # pylint: disable=too-many-public-methods

    def __init__(self):
        super(NodeManager, self).__init__()

        self._nodeDbApi = NodeDbApi()
        self._hardwareProfileDbApi = HardwareProfileDbApi()
        self._cm = ConfigManager()
        self._san = san.San()
        self._bhm = osUtility.getOsObjectFactory().getOsBootHostManager()

    def __validateHostName(self, hostname: str, name_format: str) -> NoReturn:
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
                      dbHardwareProfile: HardwareProfile,
                      dbSoftwareProfile: Optional[SoftwareProfile] = None,
                      validateIp: bool = True, bGenerateIp: bool = True,
                      dns_zone: Optional[str] = None) -> Node:
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

        # This is where the Node() object is first created.
        node = Node()

        # Set the default node state
        node.state = 'Discovered'

        if 'rack' in addNodeRequest:
            node.rack = addNodeRequest['rack']

        node.addHostSession = addNodeRequest['addHostSession']

        hostname = addNodeRequest['name'] \
            if 'name' in addNodeRequest else None

        # Ensure no conflicting options (ie. specifying host name for
        # hardware profile in which host names are generated)
        self.__validateHostName(hostname, dbHardwareProfile.nameFormat)

        node.name = hostname

        # Complete initialization of new node record
        nic_defs = addNodeRequest['nics'] \
            if 'nics' in addNodeRequest else []

        AddHostServerLocal().initializeNode(
            session, node, dbHardwareProfile, dbSoftwareProfile, nic_defs,
            bValidateIp=validateIp, bGenerateIp=bGenerateIp,
            dns_zone=dns_zone)

        # Set hardware profile of new node
        node.hardwareProfileId = dbHardwareProfile.id

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

    def getNode(self, name, optionDict=None):
        """Get node by name"""

        optionDict_ = optionDict.copy() if optionDict else {}

        optionDict_.update({'hardwareprofile': True})

        node = self._nodeDbApi.getNode(name, optionDict_)

        hwprofile = self._hardwareProfileDbApi.getHardwareProfile(
            node.getHardwareProfile().getName(), {'resourceadapter': True})

        adapter_name = hwprofile.getResourceAdapter().getName() \
            if hwprofile.getResourceAdapter() else 'default'

        # Query vcpus from resource adapter
        ResourceAdapterClass = resourceAdapterFactory.getResourceAdapterClass(
            adapter_name)

        # Update Node object
        node.setVcpus(ResourceAdapterClass().get_node_vcpus(node.getName()))

        return node

    def getNode_json(self, session: Session, name: str) -> NodeModel:
        """
        Get node by name
        """
        node = NodesDbHandler().getNode(session, name)

        node_dict = NodeSchema().dump(node).data

        if node.hardwareprofile.resourceadapter:
            resource_adapter_api = resourceAdapterFactory.getApi(
                node.hardwareprofile.resourceadapter.name
            )

            # Query vcpus from resource adapter
            node_dict['vcpus'] = resource_adapter_api.get_node_vcpus(name)

        return node_dict

    def getNodeById(self, nodeId, optionDict=None):
        """
        Get node by node id

        Raises:
            NodeNotFound
        """
        return self._nodeDbApi.getNodeById(int(nodeId), optionDict)

    def getNodeByIp(self, ip):
        """
        Get node by IP address

        Raises:
            NodeNotFound
        """

        return self._nodeDbApi.getNodeByIp(ip)

    def getNodeList(self, tags=None):
        """Return all nodes"""
        return self._nodeDbApi.getNodeList(tags=tags)

    def updateNode(self, nodeName, updateNodeRequest):
        self.getLogger().debug('updateNode(): name=[{0}]'.format(nodeName))

        session = DbManager().openSession()

        try:
            node = NodesDbHandler().getNode(session, nodeName)

            if 'nics' in updateNodeRequest:
                nic = updateNodeRequest['nics'][0]

                if 'ip' in nic:
                    node.nics[0].ip = nic['ip']
                    node.nics[0].boot = True

            # Call resource adapter
            NodesDbHandler().updateNode(session, node, updateNodeRequest)

            run_post_install = False

            if 'state' in updateNodeRequest:
                run_post_install = node.state == 'Allocated' and \
                    updateNodeRequest['state'] == 'Provisioned'

                node.state = updateNodeRequest['state']

            session.commit()

            if run_post_install:
                self.getLogger().debug(
                    'updateNode(): run-post-install for node [{0}]'.format(
                        node.name))

                self.__scheduleUpdate()
        except Exception:
            session.rollback()

            self.getLogger().exception(
                'Exception updating node [{0}]'.format(nodeName))
        finally:
            DbManager().closeSession()

    def updateNodeStatus(self, nodeName, state=None, bootFrom=None):
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
            'updateNodeStatus(): node=[%s], state=[%s], bootFrom=[%s]' % (
                nodeName, state, value))

        session = DbManager().openSession()

        try:
            dbNode = NodesDbHandler().getNode(session, nodeName)

            # Bitfield representing node changes (0 = state change, 1 = bootFrom
            # change)
            changed = 0

            if state is not None and state != dbNode.state:
                # 'state' changed
                changed |= 1

            if bootFrom is not None and bootFrom != dbNode.bootFrom:
                # 'bootFrom' changed
                changed |= 2

            if changed:
                # Create custom log message
                msg = 'Node [%s] state change:' % (dbNode.name)

                if changed & 1:
                    msg += ' state: [%s] -> [%s]' % (dbNode.state, state)

                    dbNode.state = state

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
            # not marked as 'remote' and we're not acting on the installer node.
            if dbNode.softwareprofile and \
                    dbNode.softwareprofile.type != 'installer' and \
                    dbNode.hardwareprofile.location != 'remote':
                # update local boot configuration for on-premise nodes
                self._bhm.writePXEFile(dbNode, localboot=bootFrom)

            session.commit()

            return result
        finally:
            DbManager().closeSession()

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

    def deleteNode(self, nodespec):
        """
        Delete node by nodespec

        Raises:
            NodeNotFound
        """

        installer_hostname = socket.getfqdn().split('.', 1)[0]

        session = DbManager().openSession()

        try:
            nodes = []

            for node in self.__expand_nodespec(session, nodespec):
                if node.name.split('.', 1)[0] == installer_hostname:
                    self.getLogger().info(
                        'Ignoring request to delete installer node'
                        ' ([{0}])'.format(node.name))

                    continue

                nodes.append(node)

            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            self.__preDeleteHost(nodes)

            nodeErrorDict = NodesDbHandler().deleteNode(session, nodes)

            # REALLY!?!? Convert a list of Nodes objects into a list of
            # node names so we can report the list back to the end-user.
            # This needs to be FIXED!

            result, nodes_deleted = self.__process_nodeErrorDict(nodeErrorDict)

            session.commit()

            # ============================================================
            # Perform actions *after* node deletion(s) have been committed
            # to database.
            # ============================================================

            self.__postDeleteHost(nodes_deleted)

            addHostSessions = set([tmpnode['addHostSession']
                                   for tmpnode in nodes_deleted])

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
        except TortugaException:
            session.rollback()

            raise
        except Exception:
            session.rollback()

            self.getLogger().exception('Exception in NodeManager.deleteNode()')

            raise
        finally:
            DbManager().closeSession()

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

    def __preDeleteHost(self, nodes):
        self.getLogger().debug(
            '__preDeleteHost(): nodes=[%s]' % (
                ' '.join([node.name for node in nodes])))

        if not nodes:
            self.getLogger().debug('No nodes deleted in this operation')

            return

        kitmgr = KitActionsManager()

        for node in nodes:
            kitmgr.pre_delete_host(
                node.hardwareprofile.name,
                node.softwareprofile.name if node.softwareprofile else None,
                nodes=[node.name])

    def __postDeleteHost(self, nodes_deleted):
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

        kitmgr = KitActionsManager()

        for node_dict in nodes_deleted:
            kitmgr.post_delete_host(
                node_dict['hardwareprofile'],
                node_dict['softwareprofile']
                if 'softwareprofile' in node_dict else None,
                nodes=[node_dict['name']])

    def __scheduleUpdate(self):
        tortugaSubprocess.executeCommand(
            os.path.join(self._cm.getRoot(), 'bin/schedule-update'))

    def getInstallerNode(self, optionDict=None):
        return self._nodeDbApi.getNode(
            self._cm.getInstaller(), optionDict=optionDict)

    def getProvisioningInfo(self, nodeName):
        return self._nodeDbApi.getProvisioningInfo(nodeName)


    def __transferNodeCommon(self, session, dbDstSoftwareProfile,
                             results): \
            # pylint: disable=no-self-use
        # Aggregate list of transferred nodes based on hardware profile
        # to call resource adapter minimal number of times.

        hwProfileMap = {}

        for transferResultDict in results:
            dbNode = transferResultDict['node']
            dbHardwareProfile = dbNode.hardwareprofile

            if dbHardwareProfile not in hwProfileMap:
                hwProfileMap[dbHardwareProfile] = [transferResultDict]
            else:
                hwProfileMap[dbHardwareProfile].append(transferResultDict)

        session.commit()

        nodeTransferDict = {}

        # Kill two birds with one stone... do the resource adapter
        # action as well as populate the nodeTransferDict. This saves
        # having to iterate twice on the same result data.
        for dbHardwareProfile, nodesDict in hwProfileMap.items():
            adapter = resourceAdapterFactory.getApi(
                dbHardwareProfile.resourceadapter.name)

            dbNodeTuples = []

            for nodeDict in nodesDict:
                dbNode = nodeDict['node']
                dbSrcSoftwareProfile = nodeDict['prev_softwareprofile']

                if dbSrcSoftwareProfile.name not in nodeTransferDict:
                    nodeTransferDict[dbSrcSoftwareProfile.name] = {
                        'added': [],
                        'removed': [dbNode],
                    }
                else:
                    nodeTransferDict[dbSrcSoftwareProfile.name]['removed'].\
                        append(dbNode)

                if dbDstSoftwareProfile.name not in nodeTransferDict:
                    nodeTransferDict[dbDstSoftwareProfile.name] = {
                        'added': [dbNode],
                        'removed': [],
                    }
                else:
                    nodeTransferDict[dbDstSoftwareProfile.name]['added'].\
                        append(dbNode)

                # The destination software profile is available through
                # node relationship.
                dbNodeTuples.append((dbNode, dbSrcSoftwareProfile))

            adapter.transferNode(dbNodeTuples, dbDstSoftwareProfile)

            session.commit()

        # Now call the 'refresh' action to all participatory components
        KitActionsManager().refresh(nodeTransferDict)

        return results

    def transferNode(self, nodespec, dstSoftwareProfileName, bForce=False):
        """
        Transfer nodes defined by 'nodespec' to 'dstSoftwareProfile'

        Raises:
            NodeNotFound
            SoftwareProfileNotFound
            NodeTransferNotValid
        """

        session = DbManager().openSession()

        try:
            nodes = self.__expand_nodespec(session, nodespec)

            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            dbDstSoftwareProfile = SoftwareProfilesDbHandler().\
                getSoftwareProfile(session, dstSoftwareProfileName)

            results = NodesDbHandler().transferNode(
                session, nodes, dbDstSoftwareProfile, bForce=bForce)

            return self.__transferNodeCommon(
                session, dbDstSoftwareProfile, results)
        finally:
            DbManager().closeSession()

    def transferNodes(self, srcSoftwareProfileName, dstSoftwareProfileName,
                      count, bForce=False):
        """
        Transfer 'count' nodes from 'srcSoftwareProfile' to
        'dstSoftwareProfile'

        Raises:
            SoftwareProfileNotFound
        """

        session = DbManager().openSession()

        try:
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

            results = NodesDbHandler().transferNodes(
                session, dbSrcSoftwareProfile, dbDstSoftwareProfile,
                int(float(count)), bForce=bForce)

            return self.__transferNodeCommon(
                session, dbDstSoftwareProfile, results)
        finally:
            DbManager().closeSession()

    def idleNode(self, nodespec):
        """
        Raises:
            NodeNotFound
        """

        session = DbManager().openSession()

        try:
            nodes = self.__expand_nodespec(session, nodespec)

            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            result = NodesDbHandler().idleNode(session, nodes)

            # Convert list of Nodes to list of node names for providing
            # user feedback.

            result_dict = {}
            for key, dbNodes in result.items():
                result_dict[key] = [dbNode.name for dbNode in dbNodes]

            session.commit()

            # Remove Puppet certificate(s) for idled node(s)
            for node_name in result_dict['success']:
                # Remove Puppet certificate for idled node
                self._bhm.deletePuppetNodeCert(node_name)

            # Schedule a cluster update
            self.__scheduleUpdate()

            return result_dict
        except TortugaException as ex:
            session.rollback()

            raise
        except Exception as ex:
            session.rollback()

            self.getLogger().exception(
                '[%s] %s' % (self.__class__.__name__, ex))

            raise
        finally:
            DbManager().closeSession()

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

    def activateNode(self, nodespec, softwareProfileName):
        """
        Raises:
            SoftwareProfileNotFound
            NodeNotFound
            TortugaException
        """

        session = DbManager().openSession()

        try:
            dbSoftwareProfile = SoftwareProfilesDbHandler().\
                getSoftwareProfile(session, softwareProfileName) \
                if softwareProfileName else None

            dbNodes = self.__expand_nodespec(session, nodespec)

            if not dbNodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            tmp_results = NodesDbHandler().activateNode(
                session, dbNodes, dbSoftwareProfile)

            results = self.__process_activateNode_results(
                tmp_results, softwareProfileName)

            session.commit()

            # Schedule a cluster update
            self.__scheduleUpdate()

            return results
        except TortugaException as ex:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
        finally:
            DbManager().closeSession()

    def startupNode(self, nodespec, remainingNodeList=None, bootMethod='n'):
        """
        Raises:
            NodeNotFound
        """

        return self._nodeDbApi.startupNode(
            nodespec, remainingNodeList=remainingNodeList or [],
            bootMethod=bootMethod)

    def shutdownNode(self, nodespec, bSoftShutdown=False):
        """
        Raises:
            NodeNotFound
        """

        return self._nodeDbApi.shutdownNode(nodespec, bSoftShutdown)

    def build_node_filterspec(self, nodespec):
        filter_spec = []

        for nodespec_token in nodespec.split(','):
            # Convert shell-style wildcards into SQL wildcards
            if '*' in nodespec_token or '?' in nodespec_token:
                filter_spec.append(
                    nodespec_token.replace('*', '%').replace('?', '_'))

                continue

            if '.' not in nodespec_token:
                filter_spec.append(nodespec_token)
                filter_spec.append(nodespec_token + '.%')

                continue

            # Add nodespec "AS IS"
            filter_spec.append(nodespec_token)

        return filter_spec

    def __expand_nodespec(self, session, nodespec): \
            # pylint: disable=no-self-use
        # Expand wildcards in nodespec. Each token in the nodespec can
        # be wildcard that expands into one or more nodes.

        return NodesDbHandler().getNodesByNameFilter(
            session, self.build_node_filterspec(nodespec))

    def rebootNode(self, nodespec, bSoftReset=False, bReinstall=False):
        """
        Raises:
            NodeNotFound
        """

        session = DbManager().openSession()

        try:
            nodes = self.__expand_nodespec(session, nodespec)
            if not nodes:
                raise NodeNotFound(
                    'No nodes matching nodespec [%s]' % (nodespec))

            if bReinstall:
                for dbNode in nodes:
                    self._bhm.setNodeForNetworkBoot(dbNode)

            results = NodesDbHandler().rebootNode(
                session, nodes, bSoftReset)

            session.commit()

            return results
        finally:
            DbManager().closeSession()

    def checkpointNode(self, nodeName):
        return self._nodeDbApi.checkpointNode(nodeName)

    def revertNodeToCheckpoint(self, nodeName):
        return self._nodeDbApi.revertNodeToCheckpoint(nodeName)

    def migrateNode(self, nodeName, remainingNodeList, liveMigrate):
        return self._nodeDbApi.migrateNode(
            nodeName, remainingNodeList, liveMigrate)

    def evacuateChildren(self, nodeName):
        self._nodeDbApi.evacuateChildren(nodeName)

    def getChildrenList(self, nodeName):
        return self._nodeDbApi.getChildrenList(nodeName)

    def setParentNode(self, nodeName, parentNodeName):
        self._nodeDbApi.setParentNode(nodeName, parentNodeName)

    def addStorageVolume(self, nodeName: str, volume: str,
                         isDirect: Optional[str] = "DEFAULT") -> NoReturn:
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

        api = resourceAdapterFactory.getApi(
            node.getHardwareProfile().getResourceAdapter().getName())

        if isDirect == "DEFAULT":
            api.addVolumeToNode(node, volume)

        api.addVolumeToNode(node, volume, isDirect)

    def removeStorageVolume(self, nodeName: str, volume: str) -> NoReturn:
        """
        Raises:
            VolumeDoesNotExist
            UnsupportedOperation
        """

        node = self.getNode(nodeName, {'hardwareprofile': True})

        api = resourceAdapterFactory.getApi(
            node.getHardwareProfile().getResourceAdapter().getName())

        vol = self._san.getVolume(volume)

        if vol is None:
            raise VolumeDoesNotExist(
                'The volume [%s] does not exist' % (volume))

        if not vol.getPersistent():
            raise UnsupportedOperation(
                'Only persistent volumes can be detached')

        api.removeVolumeFromNode(node, volume)

    def getStorageVolumes(self, nodeName: str):
        return self._san.getNodeVolumes(self.getNode(nodeName).getName())

    def getNodesByNodeState(self, state: str):
        return self._nodeDbApi.getNodesByNodeState(state)

    def getNodesByNameFilter(self, _filter: str):
        return self._nodeDbApi.getNodesByNameFilter(_filter)
