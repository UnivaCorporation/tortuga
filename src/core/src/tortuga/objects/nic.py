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

from tortuga.objects.network import Network
from tortuga.objects.networkDevice import NetworkDevice
from tortuga.objects.tortugaObject import TortugaObject
from tortuga.utility.helper import str2bool


class Nic(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'nic'

    def __init__(self, mac=None, ip=None):
        TortugaObject.__init__(
            self, {
                'mac': mac,
                'ip': ip
            }, ['mac', 'ip', 'id'], Nic.ROOT_TAG)

    def __repr__(self):
        return '%s (%s/%s)' % (
            self.getNetworkDevice().getName(), self.getIp(), self.getMac())

    def setNetworkDevice(self, device):
        """Set network device"""
        self['networkdevice'] = device

    def getNetworkDevice(self):
        return self.get('networkdevice')

    def setNetworkDeviceId(self, networkDeviceId):
        """Set network device id"""
        self['networkDeviceId'] = networkDeviceId

    def getNetworkDeviceId(self):
        return self.get('networkDeviceId')

    def setId(self, id_):
        """ Set nic id."""
        self['id'] = id_

    def getId(self):
        """ Return nic id. """
        return self.get('id')

    def setNodeId(self, nodeId):
        """ Set nodeId."""
        self['nodeId'] = nodeId

    def getNodeId(self):
        """ Return nodeId. """
        return self.get('nodeId')

    def setNetworkId(self, networkId):
        """ Set networkId."""
        self['networkId'] = networkId

    def getNetworkId(self):
        """ Return networkId. """
        return self.get('networkId')

    def setMac(self, mac):
        """ Set mac."""
        self['mac'] = mac

    def getMac(self):
        """ Return mac. """
        return self.get('mac')

    def setIp(self, ip):
        """ Set ip."""
        self['ip'] = ip

    def getIp(self):
        """ Return ip. """
        return self.get('ip')

    def setBoot(self, boot):
        """ Set boot."""
        self['boot'] = str2bool(boot)

    def getBoot(self):
        """ Return boot. """
        return str2bool(self.get('boot'))

    def setNetwork(self, network):
        self['network'] = network

    def getNetwork(self):
        return self.get('network')

    @staticmethod
    def getKeys():
        return ['id', 'nodeId', 'networkId', 'mac', 'ip', 'boot']

    @classmethod
    def getFromDict(cls, _dict):
        """ Get nic from _dict. """

        nic = super(Nic, cls).getFromDict(_dict)

        networkDict = _dict.get(Network.ROOT_TAG)

        if networkDict:
            nic.setNetwork(Network.getFromDict(networkDict))

        networkDeviceDict = _dict.get(NetworkDevice.ROOT_TAG)

        if networkDeviceDict:
            nic.setNetworkDevice(
                NetworkDevice.getFromDict(networkDeviceDict))

        return nic

    @classmethod
    def getFromDbDict(cls, _dict):
        nic = super(Nic, cls).getFromDict(_dict)

        # network (relation)
        networkDict = _dict.get(Network.ROOT_TAG)

        if networkDict:
            nic.setNetwork(Network.getFromDbDict(networkDict.__dict__))

        # networkdevice (relation)
        networkDeviceDict = _dict.get(NetworkDevice.ROOT_TAG)

        if networkDeviceDict:
            nic.setNetworkDevice(
                NetworkDevice.getFromDbDict(networkDeviceDict.__dict__))

        return nic
