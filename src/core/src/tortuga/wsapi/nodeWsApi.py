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
from typing import List, Optional, Union

import tortuga.objects.node
import tortuga.objects.provisioningInfo
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.tortugaObject import TortugaObjectList

from .tortugaWsApi import TortugaWsApi


class NodeWsApi(TortugaWsApi):
    """
    Node WS API class.
    """

    def getNodeList(self, nodespec: Optional[Union[str, None]] = None,
                    tags: Optional[Union[dict, None]] = None,
                    addHostSession: Optional[Union[str, None]] = None):
        """
        Get list of nodes

            Returns:
               a list of nodes
            Throws:
                TortugaException
        """

        url = 'nodes/'

        if nodespec:
            url += '?name={}'.format(nodespec)

        if addHostSession:
            url += '?addHostSession={}'.format(addHostSession)

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
            responseDict = self.get(url)
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
        url = 'nodes/?name=%s' % (urllib.parse.quote(name))

        if optionDict:
            for key, value in optionDict.items():
                if not value:
                    continue
                url += '&include={}'.format(key)

        try:
            responseDict = self.get(url)

            if not responseDict['nodes']:
                raise NodeNotFound(
                    'No nodes matching nodespec [{}]'.format(name))

            if len(responseDict['nodes']) > 1:
                raise InvalidArgument(
                    'Nodespec [{}] returned multiple results for a single'
                    ' node request; use getNodeList()'.format(name))

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

        url = 'nodes/?installer=true'

        try:
            responseDict = self.get(url)
            
            return tortuga.objects.node.Node.getFromDict(
                responseDict['nodes'][0])
        
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNodeById(self, nodeId: int,
                    optionDict: Optional[Union[dict, None]] = None): \
            # pylint: disable=unused-argument
        url = 'nodes/%d' % (int(nodeId))

        if optionDict:
            for key, value in optionDict.items():
                if not value:
                    continue
                url += '&include={}'.format(key)

        try:
            responseDict = self.get(url)

            return tortuga.objects.node.Node.getFromDict(
                responseDict.get('node'))
        
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteNode(self, nodespec: str, force: bool = False) -> dict:
        url = 'nodes/%s' % (urllib.parse.quote_plus(nodespec))

        url += '?force={}'.format('true' if force else 'false')

        try:
            responseDict = self.delete(url)

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

        url = 'nodes/?ip={}'.format(urllib.parse.quote_plus(ip))

        try:
            responseDict = self.get(url)

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

        url = 'nodes/%s' % (urllib.parse.quote_plus(name))

        postdata = {}

        if state is not None:
            postdata['state'] = state

        if bootFrom is not None:
            postdata['bootFrom'] = bootFrom

        try:
            self.put(url, postdata)
            
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

        url = 'nodes/%s/provisioningInfo' % (
            urllib.parse.quote_plus(nodeName))

        try:
            responseDict = self.get(url)

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

    def idleNode(self, nodespec):
        """
        idle node
        """

        url = 'nodes/%s/idle' % (urllib.parse.quote_plus(nodespec))

        try:
            responseDict = self.get(url)

            return responseDict
        
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def activateNode(self, nodeName, softwareProfileName):
        """
        activate node
        """

        url = 'nodes/%s/activate' % (nodeName)

        postdata = {}

        if softwareProfileName:
            postdata['softwareProfileName'] = softwareProfileName

        try:
            responseDict = self.post(url, postdata)

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

        url = 'nodes/%s/startup/%s/boot/%s' % (
            nodespec, nodeString, bootMethod)

        try:
            self.put(url, {})
            
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

        url = 'nodes/%s/shutdown' % (urllib.parse.quote_plus(nodespec))

        try:
            self.get(url)
            
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def rebootNode(self, nodespec: str, bSoftReset: Optional[bool] = True,
                   bReinstall: Optional[bool] = False):
        """
        reboot node
        """

        url = 'nodes/{}/reset?hard={}&reinstall={}'.format(
            urllib.parse.quote_plus(nodespec),
            '0' if bSoftReset else '1',
            '1' if bReinstall else '0')

        try:
            self.put(url)
            
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getNodeRequests(self, addHostSession: Optional[Union[str, None]] = None):
        url = 'addhost/requests/'

        if addHostSession:
            url += '?addHostSession={}'.format(
               urllib.parse.quote_plus(addHostSession)
            )

        try:
            responseDict = self.get(url)

            return responseDict
        
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def transferNode(self, nodespec: str, softwareProfileName: str,
                     bForce: bool = False):
        """
        Transfer named node
        """

        url = 'transfer-node/{}'.format(urllib.parse.quote_plus(nodespec))

        request = {
            'softwareProfileName': softwareProfileName,
            'bForce': bForce,
        }

        try:
            return self.put(url, request)[1]
        
        except Exception as exc:  # noqa pylint: disable=broad-except
            if not isinstance(exc, TortugaException):
                raise TortugaException(exception=exc)
            raise

    def transferNodes(self, srcSoftwareProfile: str,
                      dstSoftwareProfile: str, count: int,
                      bForce: bool = False):
        """
        Transfer node(s) between software profiles
        """

        url = 'transfer-nodes/'

        request = {
            'srcSoftwareProfile': srcSoftwareProfile,
            'dstSoftwareProfile': dstSoftwareProfile,
            'count': count,
            'bForce': bForce,
        }

        try:
            return self.put(url, request)[1]
        
        except Exception as exc:  # noqa pylint: disable=broad-except
            if not isinstance(exc, TortugaException):
                raise TortugaException(exception=exc)
            raise
