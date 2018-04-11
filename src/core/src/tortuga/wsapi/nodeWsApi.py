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

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Union

import tortuga.objects.node
import tortuga.objects.provisioningInfo
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.tortugaObject import TortugaObjectList

from .tortugaWsApi import TortugaWsApi


class NodeWsApi(TortugaWsApi):
    """
    Node WS API class.
    """

    def getNodeList(self, tags=None):
        """
        Get list of nodes

            Returns:
               a list of nodes
            Throws:
                TortugaException
        """

        url = 'v1/nodes'

        if tags:
            params = []

            for key, value in tags.items():
                if value is None:
                    params.append(urllib.parse.urlencode({'tag': key}))
                else:
                    params.append(
                        urllib.parse.urlencode({'tag': '{0}={1}'.format(
                            key, value)}))

            if params:
                url += '?' + '&'.join(params)

        try:
            _, responseDict = self.sendSessionRequest(url)

            nodeList = TortugaObjectList()

            if 'nodes' in responseDict:
                for cDict in responseDict['nodes']:
                    node = tortuga.objects.node.Node.getFromDict(cDict)

                    nodeList.append(node)
            else:
                node = tortuga.objects.node.Node.getFromDict(
                    responseDict.get('node'))

                nodeList.append(node)

            return nodeList
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNode(self, name,
                optionDict: Optional[Union[dict, None]] = None): \
            # pylint: disable=unused-argument
        url = 'v1/nodes?name=%s' % (urllib.parse.quote(name))

        if optionDict:
            for key, value in optionDict.items():
                if not value:
                    continue
                url += '&include={}'.format(key)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.node.Node.getFromDict(
                responseDict.get('nodes')[0])
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getInstallerNode(self, optionDict=None): \
            # pylint: disable=unused-argument
        """
        Helper method to get installer node without having to do
        multiple REST API calls
        """

        url = 'v1/nodes?installer=true'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.node.Node.getFromDict(
                responseDict['nodes'][0])
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNodeById(self, nodeId: int,
                    optionDict: Optional[Union[dict, None]] = None): \
            # pylint: disable=unused-argument
        url = 'v1/nodes/%d' % (int(nodeId))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.node.Node.getFromDict(
                responseDict.get('node'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteNode(self, nodespec):
        url = 'v1/nodes/%s' % (urllib.parse.quote_plus(nodespec))

        try:
            _, responseDict = self.sendSessionRequest(url, method='DELETE')

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNodeByIp(self, ip: str):
        """
        This API is called by compute nodes to get the node record
        associated with an IP
        """

        url = 'v1/nodes?ip={}'.format(urllib.parse.quote_plus(ip))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.node.Node.getFromDict(
                responseDict.get('nodes')[0])
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateNodeStatus(self, name: str,
                         state: Optional[Union[str, None]] = None,
                         bootFrom: Optional[Union[int, None]] = None):
        """
        updateNodeStatus() is really a "constrained" (only two fields
        supported) updateNode() request
        """

        url = 'v1/nodes/%s' % (urllib.parse.quote_plus(name))

        postdata = {}

        if state is not None:
            postdata['state'] = state

        if bootFrom is not None:
            postdata['bootFrom'] = bootFrom

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(postdata))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getProvisioningInfo(self, nodeName: str):
        """
        Get the provisioning information for a given provisioned address

            Returns:
                [provisioningInformation structure]
            Throws:
                NodeNotFound
                DbError
        """

        url = 'v1/nodes/%s/provisioningInfo' % (
            urllib.parse.quote_plus(nodeName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            if 'provisioninginfo' not in responseDict:
                return None

            pInfoDict = responseDict.get('provisioninginfo')

            # This call will handle everything except nested XML lists
            info = tortuga.objects.provisioningInfo.ProvisioningInfo.\
                getFromDict(pInfoDict)

            return info
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def setParentNode(self, nodeName, parentNodeName):
        """
        Set parent node of specified node
        """

        url = 'v1/nodes/%s/parentNode' % (
            urllib.parse.quote_plus(nodeName))

        try:
            response, _ = self.sendSessionRequest(
                url, method='POST',
                data=json.dumps(dict(parentNodeName=parentNodeName)))

            return response
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def idleNode(self, nodespec):
        """
        idle node
        """

        url = 'v1/nodes/%s/idle' % (urllib.parse.quote_plus(nodespec))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def activateNode(self, nodeName, softwareProfileName):
        """
        activate node
        """

        url = 'v1/nodes/%s/activate' % (nodeName)

        postdata = {}

        if softwareProfileName:
            postdata['softwareProfileName'] = softwareProfileName

        try:
            _, responseDict = self.sendSessionRequest(
                url, method='POST', data=json.dumps(postdata))

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def startupNode(self, nodespec: str,
                    remainingNodeList: Optional[Union[List[str], None]] = None,
                    bootMethod: str = 'n'):
        """
        startup node
        """

        # Turn 'nodeList' into something that can be passed in
        nodeString = '+'.join(remainingNodeList) if remainingNodeList else '+'

        url = 'v1/nodes/%s/startup/%s/boot/%s' % (
            nodespec, nodeString, bootMethod)

        try:
            self.sendSessionRequest(url, method='PUT')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def shutdownNode(self, nodespec,
                     bSoftShutdown: Optional[bool] = False): \
            # pylint: disable=unused-argument
        """
        shutdown node
        """

        url = 'v1/nodes/%s/shutdown' % (urllib.parse.quote_plus(nodespec))

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def rebootNode(self, nodespec, bSoftReset: Optional[bool] = True,
                   bReinstall: Optional[bool] = False): \
            # pylint: disable=unused-argument
        """
        reboot node
        """

        url = 'v1/nodes/%s/reboot' % (urllib.parse.quote_plus(nodespec))

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def evacuateChildren(self, nodeName):
        """
        evacuate any children of this node
        """

        url = 'v1/nodes/%s/evacuate' % (urllib.parse.quote_plus(nodeName))

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getChildrenList(self, nodeName: str):
        """
        return the list of children currently on this node
        """

        url = 'v1/nodes/%s/children' % (urllib.parse.quote_plus(nodeName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            nodeList = TortugaObjectList()

            if responseDict:
                if 'nodes' in responseDict:
                    cDicts = responseDict.get('nodes')
                    for cDict in cDicts:
                        node = tortuga.objects.node.Node.getFromDict(cDict)
                        nodeList.append(node)
                else:
                    node = tortuga.objects.node.Node.getFromDict(
                        responseDict.get('node'))

                    nodeList.append(node)

            return nodeList
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def checkpointNode(self, nodeName):
        """
        checkpoint node
        """

        url = 'v1/nodes/%s/checkpoint' % (urllib.parse.quote_plus(nodeName))

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def revertNodeToCheckpoint(self, nodeName):
        """
        revert node to checkpoint
        """

        url = 'v1/nodes/%s/revert' % (urllib.parse.quote_plus(nodeName))

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def migrateNode(self, nodeName,
                    remainingNodeList: Optional[Union[List[str], None]],
                    liveMigrate: bool):
        """
        migrate node
        """

        # Turn remainingNodeList into something that can be passed in
        remainingNodeString = str.join('+', remainingNodeList)

        url = 'v1/nodes/%s/migrate/%s/type/%s' % (
            urllib.parse.quote_plus(nodeName), remainingNodeString,
            liveMigrate)

        try:
            self.sendSessionRequest(url)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
