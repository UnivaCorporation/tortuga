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

# pylint: disable=no-member,too-many-public-methods

from typing import List, NoReturn, Optional, Union

from sqlalchemy.orm.session import Session

from tortuga.db.hardwareProfiles import HardwareProfiles
from tortuga.db.nodes import Nodes
from tortuga.db.softwareProfiles import SoftwareProfiles
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.node.nodeManager import NodeManager
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.utility.tortugaApi import TortugaApi


class NodeApi(TortugaApi):
    """
    High-level API for performing node operations
    """
    def __init__(self):
        super(NodeApi, self).__init__()

        self._nodeManager = NodeManager()

    def createNewNode(self, session: Session, addNodeRequest: dict,
                      dbHardwareProfile: HardwareProfiles,
                      dbSoftwareProfile: Optional[Union[SoftwareProfiles, None]] = None,
                      validateIp: bool = True, bGenerateIp: bool = True,
                      dns_zone: Optional[str] = None) -> Nodes:
        try:
            return self._nodeManager.createNewNode(
                session, addNodeRequest, dbHardwareProfile,
                dbSoftwareProfile=dbSoftwareProfile,
                validateIp=validateIp, bGenerateIp=bGenerateIp,
                dns_zone=dns_zone)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Fatal error creating new node')

            raise TortugaException(exception=ex)

    def getNodeList(self, tags: Optional[Union[dict, None]] = None) -> List[Node]:
        """
        Get node list..

            Returns:
                list of nodes
            Throws:
                TortugaException
        """
        try:
            return self._nodeManager.getNodeList(tags=tags)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Fatal error retrieving node list')

            raise TortugaException(exception=ex)

    def getNode(self, name: str, optionDict: Optional[Union[dict, None]] = None):
        """Get node id by name"""
        try:
            return self._nodeManager.getNode(name, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node [{}]'.format(name))

            raise TortugaException(exception=ex)

    def getInstallerNode(self, optionDict: Optional[Union[dict, None]] = None) -> Node:
        """Get installer node"""
        try:
            return self._nodeManager.getInstallerNode(
                optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving installer node')

            raise TortugaException(exception=ex)

    def getNodeById(self, nodeId: int,
                    optionDict: Optional[Union[dict, None]] = None) -> Node:
        """
        Get a node by id
        """

        try:
            return self._nodeManager.getNodeById(nodeId, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node by id [{}]'.format(nodeId))

            raise TortugaException(exception=ex)

    def getNodeByIp(self, ip: str) -> Node:
        """Get a node by ip"""
        try:
            return self._nodeManager.getNodeByIp(ip)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node by ip [{}]'.format(ip))

            raise TortugaException(exception=ex)

    def deleteNode(self, nodespec: str):
        try:
            return self._nodeManager.deleteNode(nodespec)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error deleting nodespec [{}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def getProvisioningInfo(self, nodeName: str):
        """ Get provisioning information for a node """
        try:
            return self._nodeManager.getProvisioningInfo(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving provisioning info for'
                ' node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def updateNode(self, name: str, updateNodeRequest):
        try:
            return self._nodeManager.updateNode(
                name, updateNodeRequest)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error updating node [{0}]'.format(name))

            raise TortugaException(exception=ex)

    def updateNodeStatus(self, name: str, state: Optional[str] = None,
                         bootFrom: Optional[int] = None):
        try:
            return self._nodeManager.updateNodeStatus(
                name, state, bootFrom)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error updating status for node [{}]'.format(name))

            raise TortugaException(exception=ex)

    def transferNode(self, nodespec: str, softwareProfileName: str,
                     bForce: Optional[bool] = False):
        try:
            return self._nodeManager.transferNode(
                nodespec, softwareProfileName, bForce=bForce)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error transferring nodes matching nodespec'
                ' [{}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def transferNodes(self, srcSoftwareProfile: str, dstSoftwareProfile: str,
                      count: int, bForce: Optional[bool] = False):
        try:
            return self._nodeManager.transferNodes(
                srcSoftwareProfile, dstSoftwareProfile, count,
                bForce=bForce)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Fatal error transferring nodes')

            raise TortugaException(exception=ex)

    def idleNode(self, nodespec: str):
        try:
            return self._nodeManager.idleNode(nodespec)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error idling nodes matching nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def activateNode(self, nodeName: str, softwareProfileName: str):
        try:
            return self._nodeManager.activateNode(
                nodeName, softwareProfileName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error activating node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def startupNode(self, nodespec: str,
                    remainingNodeList: Optional[Union[list, None]] = None,
                    bootMethod: Optional[str] = 'n') -> NoReturn:
        try:
            self._nodeManager.startupNode(
                nodespec, remainingNodeList=remainingNodeList or [],
                bootMethod=bootMethod)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error starting node(s) matching nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def shutdownNode(self, nodespec: str,
                     bSoftShutdown: Optional[bool] = False) -> NoReturn:
        try:
            self._nodeManager.shutdownNode(nodespec, bSoftShutdown)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error shutting down node(s) matching'
                ' nodespec [{0}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def rebootNode(self, nodespec: str, bSoftReset: Optional[bool] = True,
                   bReinstall: Optional[bool] = False) -> NoReturn:
        try:
            self._nodeManager.rebootNode(
                nodespec, bSoftReset=bSoftReset, bReinstall=bReinstall)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error rebooting node(s) matching'
                ' nodespec [{0}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def checkpointNode(self, nodeName: str) -> NoReturn:
        try:
            self._nodeManager.checkpointNode(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error checkpointing node [{0}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def revertNodeToCheckpoint(self, nodeName: str) -> NoReturn:
        try:
            self._nodeManager.revertNodeToCheckpoint(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error reverting node [{}] to checkpoint'.format(
                    nodeName))

            raise TortugaException(exception=ex)

    def migrateNode(self, nodeName: str, remainingNodeList: List[Node],
                    liveMigrate: bool) -> NoReturn:
        try:
            self._nodeManager.migrateNode(
                nodeName, remainingNodeList, liveMigrate)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error migrating node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def evacuateChildren(self, nodeName: str) -> NoReturn:
        try:
            self._nodeManager.evacuateChildren(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error evacuating child node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def getChildrenList(self, nodeName: str) -> List[Node]:
        try:
            return self._nodeManager.getChildrenList(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving child node list')

            raise TortugaException(exception=ex)

    def setParentNode(self, nodeName: str, parentNodeName: str) -> NoReturn:
        try:
            self._nodeManager.setParentNode(nodeName, parentNodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error setting parent node of [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def addStorageVolume(self, nodeName: str, volume: str,
                         isDirect: Optional[str] = 'DEFAULT'):
        try:
            if isDirect == 'DEFAULT':
                return self._nodeManager.addStorageVolume(nodeName, volume)

            return self._nodeManager.addStorageVolume(
                nodeName, volume, isDirect)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error adding storage volume to node [{}]'.format(
                    nodeName))

            raise TortugaException(exception=ex)

    def removeStorageVolume(self, nodeName: str, volume: str):
        try:
            return self._nodeManager.removeStorageVolume(nodeName, volume)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error removing storage volume from node [{}]'.format(
                    nodeName))

            raise TortugaException(exception=ex)

    def getStorageVolumeList(self, nodeName: str):
        try:
            return self._nodeManager.getStorageVolumes(nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving storage volumes for node [{}]'.format(
                    nodeName))

            raise TortugaException(exception=ex)

    def getNodesByNodeState(self, state: str) -> List[Node]:
        """
        Get list of nodes in specified state

            Returns:
                list of nodes
            Throws:
                KitNotFound
                TortugaException
        """
        try:
            return self._nodeManager.getNodesByNodeState(state)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes in state [{}]'.format(state))

            raise TortugaException(exception=ex)

    def getNodesByNameFilter(self, nodespec: str,
                             optionDict: Optional[Union[dict, None]] = None) -> TortugaObjectList:
        try:
            return self._nodeManager.getNodesByNameFilter(
                nodespec, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes by nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def getNodesByAddHostSession(self, addHostSession: str, optionDict: Optional[Union[dict, None]] = None):
        try:
            return self._nodeManager.getNodesByAddHostSession(
                addHostSession, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes by add host session [{}]'.format(
                    addHostSession))

            raise TortugaException(exception=ex)
