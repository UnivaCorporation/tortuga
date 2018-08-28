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

# pylint: disable=no-member,too-many-public-methods,try-except-raise

from typing import List, Optional, Union, Dict, Tuple

from sqlalchemy.orm.session import Session

from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node as NodeModel
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.node.nodeManager import NodeManager
from tortuga.objects.node import Node
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.utility.tortugaApi import TortugaApi


Tags = List[Union[Tuple[str, str], Tuple[str]]]
OptionDict = Dict[str, bool]


class NodeApi(TortugaApi):
    """
    High-level API for performing node operations
    """
    def __init__(self):
        super(NodeApi, self).__init__()

        self._nodeManager = NodeManager()

    def createNewNode(self, session: Session, addNodeRequest: dict,
                      dbHardwareProfile: HardwareProfile,
                      dbSoftwareProfile: Optional[SoftwareProfile] = None,
                      validateIp: bool = True, bGenerateIp: bool = True,
                      dns_zone: Optional[str] = None) -> NodeModel:
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

    def getNodeList(self, session, tags: Optional[Tags] = None) \
            -> TortugaObjectList:
        """
        Get node list..

            Returns:
                list of nodes
            Throws:
                TortugaException
        """
        try:
            return self._nodeManager.getNodeList(session, tags=tags)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('Fatal error retrieving node list')

            raise TortugaException(exception=ex)

    def getNode(self, session: Session, name: str,
                optionDict: Optional[OptionDict] = None):
        """Get node id by name"""
        try:
            return self._nodeManager.getNode(
                session, name, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node [{}]'.format(name))

            raise TortugaException(exception=ex)

    def getInstallerNode(self, session,
                         optionDict: Optional[OptionDict] = None) \
            -> Node:
        """
        Get installer node
        """

        try:
            return self._nodeManager.getInstallerNode(
                session, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving installer node')

            raise TortugaException(exception=ex)

    def getNodeById(self, session: Session, nodeId: int,
                    optionDict: Optional[OptionDict] = None) -> Node:
        """
        Get a node by id
        """

        try:
            return self._nodeManager.getNodeById(
                session, nodeId, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node by id [{}]'.format(nodeId))

            raise TortugaException(exception=ex)

    def getNodeByIp(self, session: Session, ip: str) -> Node:
        """
        Get a node by ip
        """

        try:
            return self._nodeManager.getNodeByIp(session, ip)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving node by ip [{}]'.format(ip))

            raise TortugaException(exception=ex)

    def deleteNode(self, session: Session, nodespec: str, force: bool = False):
        try:
            return self._nodeManager.deleteNode(
                session, nodespec, force=force)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error deleting nodespec [{}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def getProvisioningInfo(self, session: Session, nodeName: str):
        """ Get provisioning information for a node """
        try:
            return self._nodeManager.getProvisioningInfo(session, nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving provisioning info for'
                ' node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def updateNode(self, session: Session, name: str, updateNodeRequest: dict):
        try:
            return self._nodeManager.updateNode(
                session, name, updateNodeRequest)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error updating node [{0}]'.format(name))

            raise TortugaException(exception=ex)

    def updateNodeStatus(self, session: Session, name: str,
                         state: Optional[str] = None,
                         bootFrom: Optional[int] = None):
        try:
            return self._nodeManager.updateNodeStatus(
                session, name, state, bootFrom)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error updating status for node [{}]'.format(name))

            raise TortugaException(exception=ex)

    def transferNodes(self, session: Session,
                      dstSoftwareProfile: str,
                      *,
                      count: Optional[int] = None,
                      srcSoftwareProfile: Optional[str] = None,
                      bForce: Optional[bool] = False,
                      nodespec: Optional[str] = None) -> dict:
        try:
            if nodespec:
                return self._nodeManager.transferNode(
                    session, nodespec, dstSoftwareProfile, bForce=bForce
                )

            if srcSoftwareProfile is None:
                raise TypeError(
                    'transferNodes() missing required keyword-only'
                    ' argument: \'srcSoftwareProfile\'')

            return self._nodeManager.transferNodes(
                session, srcSoftwareProfile, dstSoftwareProfile, count,
                bForce=bForce
            )
        except TortugaException:
            raise
        except Exception as ex:
            if nodespec:
                excmsg = 'Fatal error transferring nodes matching nodespec'
                ' [{}]'.format(nodespec)
            else:
                excmsg = 'Fatal error transferring nodes'

            self.getLogger().exception(excmsg)

            raise TortugaException(exception=ex)

    def idleNode(self, session: Session, nodespec: str):
        try:
            return self._nodeManager.idleNode(session, nodespec)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error idling nodes matching nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def activateNode(self, session: Session, nodeName: str,
                     softwareProfileName: str):
        try:
            return self._nodeManager.activateNode(
                session, nodeName, softwareProfileName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error activating node [{}]'.format(nodeName))

            raise TortugaException(exception=ex)

    def startupNode(self, session: Session, nodespec: str,
                    remainingNodeList: Optional[list] = None,
                    bootMethod: Optional[str] = 'n') -> None:
        try:
            self._nodeManager.startupNode(
                session, nodespec,
                remainingNodeList=remainingNodeList or [],
                bootMethod=bootMethod)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error starting node(s) matching nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def shutdownNode(self, session: Session, nodespec: str,
                     bSoftShutdown: Optional[bool] = False) -> None:
        try:
            self._nodeManager.shutdownNode(
                session, nodespec, bSoftShutdown)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error shutting down node(s) matching'
                ' nodespec [{0}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def rebootNode(self, session: Session, nodespec: str,
                   bSoftReset: Optional[bool] = True,
                   bReinstall: Optional[bool] = False) -> None:
        try:
            self._nodeManager.rebootNode(
                session, nodespec, bSoftReset=bSoftReset,
                bReinstall=bReinstall)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error rebooting node(s) matching'
                ' nodespec [{0}]'.format(nodespec))

            raise TortugaException(exception=ex)

    def addStorageVolume(self, nodeName: str, volume: str,
                         isDirect: Optional[str] = 'DEFAULT'):
        try:
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

    def getStorageVolumeList(self, session: Session, nodeName: str):
        try:
            return self._nodeManager.getStorageVolumes(session, nodeName)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving storage volumes for node [{}]'.format(
                    nodeName))

            raise TortugaException(exception=ex)

    def getNodesByNodeState(self, session: Session, state: str) \
            -> TortugaObjectList:
        """
        Get list of nodes in specified state

            Returns:
                list of nodes
            Throws:
                KitNotFound
                TortugaException
        """
        try:
            return self._nodeManager.getNodesByNodeState(session, state)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes in state [{}]'.format(state))

            raise TortugaException(exception=ex)

    def getNodesByNameFilter(self, session: Session, nodespec: str,
                             optionDict: Optional[OptionDict] = None) \
            -> TortugaObjectList:
        try:
            return self._nodeManager.getNodesByNameFilter(
                session, nodespec, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes by nodespec [{}]'.format(
                    nodespec))

            raise TortugaException(exception=ex)

    def getNodesByAddHostSession(self, session: Session,
                                 addHostSession: str,
                                 optionDict: Optional[OptionDict] = None) \
            -> TortugaObjectList:
        try:
            return self._nodeManager.getNodesByAddHostSession(
                session, addHostSession, optionDict=optionDict)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Fatal error retrieving nodes by add host session [{}]'.format(
                    addHostSession))

            raise TortugaException(exception=ex)
