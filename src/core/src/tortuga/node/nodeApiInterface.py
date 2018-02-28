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

from tortuga.exceptions.abstractMethod import AbstractMethod


class NodeApiInterface(object): \
        # pylint: disable=too-many-public-methods

    """
    Node API interface.
    """

    def getNodeList(self, tags=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get the list of nodes

            Returns:
                List of nodes.
            Throws:
                TortugaException
        """
        raise AbstractMethod(
            'getNodeList has to be implemented in the concrete API class.')

    def getNode(self, name, optionDict=None): \
            # pylint: disable=unused-argument,no-self-use
        """Get node by name"""
        raise AbstractMethod('getNode must be implemented in API class')

    def getNodeByIp(self, ip): \
            # pylint: disable=unused-argument,no-self-use
        """Get node by IP address"""
        raise AbstractMethod('getNodeByIp must be implemented in API class')

    def deleteNode(self, nodespec): \
            # pylint: disable=unused-argument,no-self-use
        """delete node by name"""
        raise AbstractMethod('deleteNode must be implemented in API class')

    def startupNode(self, nodespec, remainingNodeList=None, bootMethod='n'): \
            # pylint: disable=unused-argument,no-self-use
        """Start node"""
        raise AbstractMethod('startupNode must be implemented in API class')

    def shutdownNode(self, nodespec, bSoftShutdown=False): \
            # pylint: disable=unused-argument,no-self-use
        """Shutdown node"""
        raise AbstractMethod('shutdownNode must be implemented in API class')

    def rebootNode(self, nodespec, bSoftReset=True, bReinstall=False): \
            # pylint: disable=unused-argument,no-self-use
        """Reboot node"""
        raise AbstractMethod('rebootNode must be implemented in API class')

    def checkpointNode(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        """Checkpoint node"""
        raise AbstractMethod('checkpointNode must be implemented in API class')

    def revertNodeToCheckpoint(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        """Revert node"""
        raise AbstractMethod(
            'revertNodeToCheckpoint must be implemented in API class')

    def migrateNode(self, nodeName, remainingNodeList, liveMigrate): \
            # pylint: disable=unused-argument,no-self-use
        """Migrate node"""
        raise AbstractMethod('migrateNode must be implemented in API class')

    def getMyNode(self): \
            # pylint: disable=no-self-use
        """ get a node entry of the current node """
        raise AbstractMethod('updateNode must be implemented in API class')

    def getKickstartFile(self, node, hardwareprofile=None,
                         softwareprofile=None): \
            # pylint: disable=unused-argument,no-self-use
        """ Get the kickstart file for a given node """
        raise AbstractMethod(
            'getKickstartFile must be implemented in API class')

    def getProvisioningInfo(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        """ Get provisioning information for a node """
        raise AbstractMethod(
            'getProvisioningInfo must be implemented in API class')

    def updateNodeStatus(self, name, state=None, bootFrom=None): \
            # pylint: disable=unused-argument,no-self-use
        """update node status"""
        raise AbstractMethod(
            'updateNodeStatus must be implemented in API class')

    def transferNode(self, nodespec, softwareProfileName, bForce=False): \
            # pylint: disable=unused-argument,no-self-use
        """ Returns the nodes that were transfered """
        raise AbstractMethod('transferNode must be implemented in API class')

    def transferNodes(self, srcSoftwareProfile, dstSoftwareProfile,
                      count, bForce=False): \
            # pylint: disable=unused-argument,no-self-use
        """ Returns the nodes that were transfered """
        raise AbstractMethod(
            'transferNodes must be implemented in API class')

    def idleNode(self, nodespec): \
            # pylint: disable=unused-argument,no-self-use
        """idle node"""
        raise AbstractMethod('idleNode must be implemented in API class')

    def activateNode(self, nodeName, softwareProfileName): \
            # pylint: disable=unused-argument,no-self-use
        """activate node

        Returns software profile name
        """
        raise AbstractMethod('activateNode must be implemented in API class')

    def setParentNode(self, nodeName, parentNodeName): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'updateParentNodeId has to be implemented in the concrete API '
            'class.')

    def getNodeById(self, nodeId, optionDict=None): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'getNodeById()has to be implemented in the concrete API class.')

    def addStorageVolume(self, nodeName, volume, isDirect): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'addStorageVolume() has to be implemented in the concrete API'
            ' class')

    def removeStorageVolume(self, nodeName, volume): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'removeStorageVolume() has to be implemented in the concrete API'
            ' class')

    def getStorageVolumeList(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'getStorageVolume() has to be implemented in the'
            ' concrete API class')

    def evacuateChildren(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'evacuteChildren() has to be implemented in the'
            ' concrete API class')

    def getChildrenList(self, nodeName): \
            # pylint: disable=unused-argument,no-self-use
        raise AbstractMethod(
            'getChildrenList() has to be implemented in the'
            ' concrete API class')
