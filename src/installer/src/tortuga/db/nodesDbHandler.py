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

# pylint: disable=not-callable,no-member,multiple-statements,no-self-use

from typing import List, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.models.node import Node
from tortuga.db.models.nic import Nic
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.nodeSoftwareProfileLocked \
    import NodeSoftwareProfileLocked
from tortuga.exceptions.nodeTransferNotValid import NodeTransferNotValid
from tortuga.exceptions.profileMappingNotAllowed \
    import ProfileMappingNotAllowed
from tortuga.db.nicsDbHandler import NicsDbHandler
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.softwareUsesHardwareDbHandler \
    import SoftwareUsesHardwareDbHandler
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.models.hardwareProfileProvisioningNic \
    import HardwareProfileProvisioningNic
from tortuga.os_utility import osUtility
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.exceptions.operationFailed import OperationFailed


class NodesDbHandler(TortugaDbObjectHandler):
    """
    This class handles nodes table.
    """

    NODE_STATE_INSTALLED = 'Installed'
    NODE_STATE_DELETED = 'Deleted'

    def __init__(self):
        TortugaDbObjectHandler.__init__(self)

        self._nicsDbHandler = NicsDbHandler()
        self._hardwareProfilesDbHandler = HardwareProfilesDbHandler()
        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()
        self._softwareUsesHardwareDbHandler = SoftwareUsesHardwareDbHandler()
        self._globalParametersDbHandler = GlobalParametersDbHandler()

    def __isNodeLocked(self, dbNode):
        return dbNode.lockedState != 'Unlocked'

    def __isNodeHardLocked(self, dbNode):
        return dbNode.lockedState == 'HardLocked'

    def __isNodeSoftLocked(self, dbNode):
        return dbNode.lockedState == 'SoftLocked'

    def __getNodeState(self, dbNode):
        return dbNode.state

    def __isNodeStateDeleted(self, node):
        return self.__getNodeState(node) == NodesDbHandler.NODE_STATE_DELETED

    def __isNodeStateInstalled(self, dbNode):
        return self.__getNodeState(dbNode) == \
            NodesDbHandler.NODE_STATE_INSTALLED

    def getNode(self, session, name):
        """
        Return node.

        Raises:
            NodeNotFound
        """

        try:
            if '.' in name:
                # Attempt exact match on fully-qualfied name
                return session.query(Node).filter(
                    func.lower(Node.name) == name.lower()).one()

            # 'name' is short host name; attempt to match on either short
            # host name or any host starting with same host name
            return session.query(Node).filter(
                or_(func.lower(Node.name) == name.lower(),
                    func.lower(Node.name).like(name.lower() + '.%'))).one()
        except NoResultFound:
            raise NodeNotFound("Node [%s] not found" % (name))

    def getNodes(self, session, nodes):
        """
        This method will take either a list of Tortuga Node objects or
        node names (type 'string')
        """

        result = {
            'nodes': [],
            'badnodes': [],
        }

        for node in nodes:
            try:
                result['nodes'].append(self.getNode(session, str(node)))
            except NodeNotFound:
                result['badnodes'].append(str(node))

        return result

    def getNodesByTags(self, session, tags=[]):
        """'tags' is a list of (key, value) tuples representing tags.
        tuple may also contain only one element (key,)
        """

        searchspec = []

        # iterate over list of tag tuples making SQLAlchemy search
        # specification
        for tag in tags:
            if len(tag) == 2:
                # Match tag 'name' and 'value'
                searchspec.append(and_(Node.tags.any(name=tag[0]),
                                       Node.tags.any(value=tag[1])))
            else:
                # Match tag 'name' only
                searchspec.append(Node.tags.any(name=tag[0]))

        return session.query(Node).filter(or_(*searchspec)).all()

    def getNodesByAddHostSession(self, session, ahSession) -> List[Nodes]:
        """
        Get nodes by add host session
        Returns a list of nodes
        """

        self.getLogger().debug(
            'getNodesByAddHostSession(): ahSession [%s]' % (ahSession))

        return session.query(Node).filter(
            Node.addHostSession == ahSession).order_by(Node.name).all()

    def getNodesByNameFilter(self, session,
                             filter_spec: Union[str, list]) -> List[Node]:
        """
        Filter follows SQL "LIKE" semantics (ie. "something%")

        Returns a list of Node
        """

        filter_spec_list = [filter_spec] \
            if type(filter_spec) is not list else filter_spec

        node_filter = []

        for filter_spec_item in filter_spec_list:
            if '.' not in filter_spec_item:
                # Match exactly (ie. "hostname-01")
                node_filter.append(Node.name.like(filter_spec_item))

                # Match host name only (ie. "hostname-01.%")
                node_filter.append(Node.name.like(filter_spec_item + '.%'))

                continue

            # Match fully-qualified node names exactly
            # (ie. "hostname-01.domain")
            node_filter.append(Node.name.like(filter_spec_item))

        return session.query(Node).filter(or_(*node_filter)).all()

    def getNodeById(self, session, _id):
        """
        Return node.

        Raises:
            NodeNotFound
        """

        self.getLogger().debug('Retrieving node by ID [%s]' % (_id))

        dbNode = session.query(Node).get(_id)

        if not dbNode:
            raise NodeNotFound('Node ID [%s] not found.' % (_id))

        return dbNode

    def getNodeByIp(self, session, ip):
        """
        Raises:
            NodeNotFound
        """

        self.getLogger().debug('Retrieving node by IP [%s]' % (ip))

        try:
            return session.query(Node).join(Nic).filter(Nic.ip == ip).one()
        except NoResultFound:
            raise NodeNotFound(
                'Node with IP address [%s] not found.' % (ip))

    def getNodeList(self, session, softwareProfile=None, tags=None):
        """
        Get sorted list of nodes from the db.

        Raises:
            SoftwareProfileNotFound
        """

        self.getLogger().debug('getNodeList()')

        if softwareProfile:
            dbSoftwareProfile = self._softwareProfilesDbHandler.\
                getSoftwareProfile(session, softwareProfile)

            return dbSoftwareProfile.nodes

        searchspec = []

        if tags:
            # Build searchspec from specified tags
            for tag in tags:
                if len(tag) == 2:
                    searchspec.append(
                        and_(Node.tags.any(name=tag[0]),
                             Node.tags.any(value=tag[1])))
                else:
                    searchspec.append(Node.tags.any(name=tag[0]))

        return session.query(Node).filter(
            or_(*searchspec)).order_by(Node.name).all()

    def getNodeListByNodeStateAndSoftwareProfileName(self, session,
                                                     nodeState,
                                                     softwareProfileName):
        """
        Get list of nodes from the db.
        """

        self.getLogger().debug(
            'Retrieving nodes with state [%s] from software'
            ' profile [%s]' % (nodeState, softwareProfileName))

        return session.query(Node).join(SoftwareProfile).filter(and_(
            SoftwareProfile.name == softwareProfileName,
            Node.state == nodeState)).all()

    def evacuateChildren(self, session, dbNode):
        swProfile = dbNode.softwareprofile
        if not swProfile:
            return

        # Migrate or idle any children
        remainingNodeList = self.__getRemainingNodeList(dbNode, swProfile)

        self.__migrateOrIdleChildren(
            session, dbNode, remainingNodeList)

    def deleteNode(self, session, dbNodes):
        """
        Raises:
            DeleteNodeFailed
        """

        result = {
            'NodesDeleted': [],
            'DeleteNodeFailed': [],
            'SoftwareProfileLocked': [],
            'SoftwareProfileHardLocked': [],
        }

        nodes = {}

        for dbNode in dbNodes:
            # # Only allow nodes that are not in the installed state to
            # # be deleted if the force flag is used.
            # if not (self.__isNodeStateDeleted(dbNode) or
            #         self.__isNodeStateInstalled(dbNode)) and \
            #         not forceDelete:
            #     result['DeleteNodeFailed'].append(dbNode)
            #
            #     # Skip deleting this node
            #     continue
            #
            # # Check to see if the node is locked
            # if dbNode.lockedState == 'HardLocked':
            #     result['SoftwareProfileHardLocked'].append(dbNode)
            #
            #     # Skip deleting this node
            #     continue
            #
            # if self.__isNodeLocked(dbNode) and not forceDelete:
            #     result['SoftwareProfileLocked'].append(dbNode)
            #
            #     # Skip deleting this node
            #     continue

            # swProfile = dbNode.softwareprofile

            # if swProfile:
                # Migrate or idle any children
                # remainingNodeList = self.__getRemainingNodeList(
                #     session, dbNode, swProfile)

                # self.__migrateOrIdleChildren(
                #     session, dbNode, remainingNodeList)

                # pass

            # Mark the node as Deleted...
            dbNode.state = 'Deleted'

            if dbNode.hardwareprofile not in nodes:
                nodes[dbNode.hardwareprofile] = [dbNode]
            else:
                nodes[dbNode.hardwareprofile].append(dbNode)

        # Call resource adapter with batch(es) of node lists keyed on
        # hardware profile.

        session.commit()

        for hwProfile, dbNodeList in nodes.items():
            # Get the ResourceAdapter
            adapter = self.__getResourceAdapter(hwProfile)

            # Call the resource adapter
            adapter.deleteNode(dbNodeList)

            # Iterate over all nodes in hardware profile, completing the
            # delete operation.
            for dbNode in dbNodeList:
                # Remove PXE boot file and remove lease from dhcp server
                if hwProfile.location == 'local':
                    # Only attempt to remove local boot configuration for
                    # nodes that are marked as 'local'
                    bhm = osUtility.getOsObjectFactory().\
                        getOsBootHostManager()

                    bhm.rmPXEFile(dbNode)
                    bhm.removeDhcpLease(dbNode)

                # Iterate over nics belonging to node
                for dbNic in dbNode.nics:
                    try:
                        r = session.\
                            query(HardwareProfileProvisioningNics).\
                            filter(and_(HardwareProfileProvisioningNics.
                                        nicId == dbNic.id,
                                        HardwareProfileProvisioningNics.
                                        hardwareProfileId ==
                                        hwProfile.id)).one()

                        session.delete(r)
                    except NoResultFound:
                        pass

                # Delete all associated NICs
                for item in dbNode.nics:
                    session.delete(item)

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

    def updateNode(self, session, node, updateNodeRequest):
        """Calls updateNode() method of resource adapter"""

        adapter = self.__getResourceAdapter(node.hardwareprofile)

        adapter.updateNode(session, node, updateNodeRequest)

    def transferNode(self, session, dbNodes, newSoftwareProfile,
                     bForce=False): \
            # pylint: disable=unused-argument
        """
        Raises:
            NodeNotFound
        """

        results = []

        for node in dbNodes:
            if node.hardwareprofile not in newSoftwareProfile.\
                    hardwareprofiles:
                raise ProfileMappingNotAllowed(
                    'Node [%s] belongs to hardware profile [%s] which is'
                    ' not allowed to use software profile [%s]' % (
                        node.name, node.hardwareprofile.name,
                        newSoftwareProfile.name))

            # Check to see if the node is already using the requested
            # software profile
            if not bForce and not self.__isNodeStateInstalled(node):
                raise NodeTransferNotValid(
                    "Can't transfer node [%s], because of its state [%s]" % (
                        node.name, node.state))

            # Check to see if the node is already using the requested
            # software profile
            if node.softwareprofile == newSoftwareProfile:
                msg = 'Node [%s] is already in software profile [%s]' % (
                    node.name, newSoftwareProfile.name)

                self.getLogger().info(msg)

                raise NodeTransferNotValid(msg)

            self.getLogger().debug(
                'transferNode: Transferring node [%s] to'
                ' software profile [%s]' % (
                    node.name, newSoftwareProfile.name))

            # Check to see if the node is locked
            if self.__isNodeLocked(node):
                raise NodeSoftwareProfileLocked(
                    "Node [%s] can't be transferred while locked" % (
                        node.name))

            result = {
                'prev_softwareprofile': node.softwareprofile,
                'node': node,
            }

            node.softwareprofile = newSoftwareProfile

            results.append(result)

            # Mark nodes to be transferred
            # node.destSPId = newSoftwareProfile.id

            # Get the source software profile
            # dbSrcSoftwareProfile = node.softwareprofile

            # Migrate or idle any children
            # self.getLogger().debug(
            #     'transferNode: Migrating or idling children')

            # remainingNodeList = self.__getRemainingNodeList(
            #     session, node, dbSrcSoftwareProfile)

            # self.__transferNodes(session, [node], newSoftwareProfile)

        return results

    def __isNodeTransferrable(self, dbNode):
        # Only nodes that are not locked and in Installed state are
        # eligible for transfer.
        return not self.__isNodeLocked(dbNode) and \
            self.__isNodeStateInstalled(dbNode)

    def __getNodeTransferCandidates(self, dbSrcSoftwareProfile,
                                    dbDstSoftwareProfile, compare_func):
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

    def __getTransferrableNodes(self, dbSrcSoftwareProfile,
                                dbDstSoftwareProfile):
        """Return list of Unlocked nodes"""
        return self.__getNodeTransferCandidates(
            dbSrcSoftwareProfile, dbDstSoftwareProfile,
            self.__isNodeTransferrable)

    def __getSoftLockedNodes(self, dbSrcSoftwareProfile,
                             dbDstSoftwareProfile):
        """Return list of SoftLocked nodes"""
        return self.__getNodeTransferCandidates(
            dbSrcSoftwareProfile, dbDstSoftwareProfile,
            self.__isNodeSoftLocked)

    def transferNodes(self, session, dbSrcSoftwareProfile,
                      dbDstSoftwareProfile, count, bForce=False): \
            # pylint: disable=unused-argument
        """
        Raises:
            NodeTransferNotValid
        """

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

        return self.transferNode(session, dbNodeList, dbDstSoftwareProfile)

    def idleNode(self, session, dbNodes):
        """
        Raises:
            NodeAlreadyIdle
            NodeSoftwareProfileLocked
        """

        idleSoftwareProfilesDict = {}
        d = {}

        results = {
            'NodeAlreadyIdle': [],
            'NodeSoftwareProfileLocked': [],
            'success': [],
        }

        # Iterate over all nodes in the node spec, idling each one
        for dbNode in dbNodes:
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

            # Migrate or idle any children
            # TODO: this really isn't necessary anymore. We do not
            # provision hypervisors.
            # remainingNodeList = self.__getRemainingNodeList(
            #     session, dbNode, dbSoftwareProfile)

            # self.__migrateOrIdleChildren(
            #     session, dbNode, remainingNodeList)

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

            idleSoftwareProfilesDict[dbNode.
                                     softwareprofile.
                                     name]['idled'].append(dbNode)

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

        # Call idle action extension
        for nodeDetails in d.values():
            # Call resource adapter
            nodeState = nodeDetails['adapter'].\
                idleActiveNode(nodeDetails['nodes'])

            # Node state is consistent for all nodes within the same
            # hardware profile.
            for dbNode in nodeDetails['nodes']:
                dbNode.state = nodeState

            # Add idled node to 'success' list
            results['success'].extend(nodeDetails['nodes'])

        session.commit()

        return results

    def migrateNode(self, session, nodeName, remainingNodeList, liveMigrate):
        dbNode = self.getNode(session, nodeName)

        # Get the ResourceAdapter
        adapter = self.__getResourceAdapter(dbNode.hardwareprofile)

        # Try to migrate the Node
        self.getLogger().debug(
            'Attempting to migrate node [%s]' % (dbNode.name))

        # Call migrate action extension
        adapter.migrateNode(dbNode, remainingNodeList, liveMigrate)

    def activateNode(self, session, dbNodes,
                     dbDstSoftwareProfile=None):
        d = {}

        activateNodeResults = {
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
                softwareProfileChanged = dbNode.softwareprofile is None or \
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

            # Migrate or idle any children
            # remainingNodeList = self.__getRemainingNodeList(
            #     session, dbNode, dbSoftwareProfile)

            # self.__migrateOrIdleChildren(session, dbNode, remainingNodeList)

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
            for dbNode, softwareProfileName, bSoftwareProfileChanged in \
                    nodesDetail['nodes']:
                nodesDetail['adapter'].activateIdleNode(
                    dbNode, softwareProfileName,
                    bSoftwareProfileChanged)

                dbNode.isIdle = False

                activateNodeResults['success'].append(dbNode)

        session.commit()

        return activateNodeResults

    def __processNodeList(self, dbNodes):
        """
        Returns dict indexed by hardware profile, each with a list of
        nodes in the hardware profile
        """

        d = {}

        for dbNode in dbNodes:
            if dbNode.hardwareprofile not in d:
                d[dbNode.hardwareprofile] = {
                    'nodes': [],
                }

            d[dbNode.hardwareprofile]['nodes'].append(dbNode)

        return d

    def startupNode(self, session, nodespec, remainingNodeList=None,
                    bootMethod='n'): \
            # pylint: disable=unused-argument
        nodes = nodespec if type(nodespec) == list else [nodespec]

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

    def shutdownNode(self, session, nodespec, bSoftShutdown=False): \
            # pylint: disable=unused-argument
        nodeList = nodespec if type(nodespec) == list else [nodespec]

        d = self.__processNodeList(nodeList)

        for dbHardwareProfile, detailsDict in d.items():
            # Get the ResourceAdapter
            adapter = self.__getResourceAdapter(dbHardwareProfile)

            # Call shutdown action extension
            adapter.shutdownNode(detailsDict['nodes'], bSoftShutdown)

    def rebootNode(self, session, nodespec, bSoftReset=False): \
            # pylint: disable=unused-argument
        nodeList = nodespec if type(nodespec) == list else [nodespec]

        d = self.__processNodeList(nodeList)

        for dbHardwareProfile, detailsDict in d.items():
            adapter = self.__getResourceAdapter(dbHardwareProfile)

            # Call reboot action extension
            adapter.rebootNode(detailsDict['nodes'], bSoftReset)

    def checkpointNode(self, session, nodeName):
        # Get the Node
        dbNode = self.getNode(session, nodeName)

        # Get the ResourceAdapter
        adapter = self.__getResourceAdapter(dbNode.hardwareprofile)

        # Call checkpoint action extension
        adapter.checkpointNode(dbNode)

    def revertNodeToCheckpoint(self, session, nodeName):
        dbNode = self.getNode(session, nodeName)

        # Get the ResourceAdapter
        adapter = self.__getResourceAdapter(dbNode.hardwareprofile)

        # Call revert to checkpoint action extension
        adapter.revertNodeToCheckpoint(dbNode)

    def __getResourceAdapter(self, hardwareProfile):
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

    # def __migrateOrIdleChildren(self, session, dbNode, remainingNodeList):
    #     remainingNodeNameList = [
    #         remainingNode.name for remainingNode in remainingNodeList]
    #
    #     try:
    #         for dbChildNode in dbNode.children:
    #             migrateSucessful = False
    #
    #             if remainingNodeNameList:
    #                 try:
    #                     self.migrateNode(
    #                         session, dbChildNode.name,
    #                         remainingNodeNameList, True)
    #
    #                     migrateSucessful = True
    #                 except Exception, ex:
    #                     self.getLogger().debug(
    #                         '__migrateOrIdleChildren: Failed live migrate'
    #                         ' on %s: %s' % (dbChildNode.name, ex))
    #
    #                     migrateSucessful = False
    #
    #             if not migrateSucessful:
    #                 try:
    #                     self.idleNode(session, dbChildNode.name)
    #
    #                     self.getLogger().debug(
    #                         'Idled node [%s]' % (dbChildNode.name))
    #                 except Exception, ex:
    #                     self.getLogger().error(
    #                         '__migrateOrIdleChildren: Exception: %s on'
    #                         ' child' % (ex, dbChildNode.name))
    #             else:
    #                 self.getLogger().debug(
    #                     'Migrated node [%s]' % (dbChildNode.name))
    #     except Exception, ex:
    #         self.getLogger().error(
    #             '__migrateOrIdleChildren: Exception: %s' % (ex))

    def __getRemainingNodeList(self, dbnode, dbSoftwareProfile):
        if not dbSoftwareProfile:
            return []

        return list(set(dbSoftwareProfile.nodes) - set([dbnode]))

    def getNodesByNodeState(self, session, state):
        return session.query(Node).filter(Node.state == state).all()

    def getNodesByMac(self, session, usedMacList):
        if not usedMacList:
            return []

        return session.query(Node).join(Nic).filter(
            Nic.mac.in_(usedMacList)).all()
