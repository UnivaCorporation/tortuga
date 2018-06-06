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

from typing import Iterable, Optional

from tortuga.objects.networkDevice import NetworkDevice
from tortuga.objects.tortugaObject import TortugaObject
from tortuga.utility.helper import str2bool


class Network(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'network'

    def __init__(self, address=None):
        TortugaObject.__init__(
            self, {
                'address': address
            }, ['address', 'id'], Network.ROOT_TAG)

    def __repr__(self):
        return '%s/%s' % (self.getAddress(), self.getNetmask())

    def __eq__(self, other):
        return self.getAddress() == other.getAddress() and \
            self.getNetmask() == other.getNetmask()

    def setName(self, name):
        """ Set network name."""
        self['name'] = name

    def getName(self):
        """ Return network name. """
        return self.get('name')

    def setId(self, id_):
        """ Set network id."""
        self['id'] = id_

    def getId(self):
        """ Return network id. """
        return self.get('id')

    def setAddress(self, address):
        """ Set address."""
        self['address'] = address

    def getAddress(self):
        """ Return address. """
        return self.get('address')

    def setNetmask(self, netmask):
        """ Set netmask."""
        self['netmask'] = netmask

    def getNetmask(self):
        """ Return netmask. """
        return self.get('netmask')

    def setNetworkDevice(self, networkdevice):
        """ Set network device."""
        self['networkdevice'] = networkdevice

    def getNetworkDevice(self):
        """ Return network device. """
        return self.get('networkdevice')

    def setSuffix(self, suffix):
        """ Set suffix."""
        self['suffix'] = suffix

    def getSuffix(self):
        """ Return suffix. """
        return self.get('suffix')

    def setGateway(self, gateway):
        """ Set gateway."""
        self['gateway'] = gateway

    def getGateway(self):
        """ Return gateway. """
        return self.get('gateway')

    def setOptions(self, options):
        """ Set options."""
        self['options'] = options

    def getOptions(self):
        """ Return options. """
        return self.get('options')

    def getStartIp(self):
        """ Return startIp. """
        return self.get('startIp')

    def setStartIp(self, startIp):
        """ Set start ip."""
        self['startIp'] = startIp

    def setType(self, type_):
        """ Set type."""
        self['type'] = type_

    def getType(self):
        """ Return type. """
        return self.get('type')

    def isProvisioning(self):
        return self.getType() == 'provision'

    def setIncrement(self, increment):
        """ Set increment."""
        self['increment'] = increment

    def getIncrement(self):
        """ Return increment. """
        return self.get('increment')

    def setUsingDhcp(self, usingDhcp):
        """ Set using dhcp flag. """
        self['usingDhcp'] = str2bool(usingDhcp)

    def getUsingDhcp(self):
        """ Get using dhcp flag. """
        return str2bool(self.get('usingDhcp'))

    @staticmethod
    def getKeys():
        return [
            'id', 'address', 'netmask', 'device', 'suffix', 'gateway',
            'options', 'name', 'startIp', 'type', 'increment', 'usingDhcp']

    @classmethod
    def getFromDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        """ Get network from _dict. """

        network = super(Network, cls).getFromDict(_dict)

        networkDeviceDict = _dict.get(NetworkDevice.ROOT_TAG)

        if networkDeviceDict:
            network.setNetworkDevice(
                NetworkDevice.getFromDict(networkDeviceDict))

        return network

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        network = super(Network, cls).getFromDict(_dict, ignore=ignore)

        networkDeviceDict = _dict.get(NetworkDevice.ROOT_TAG)

        if networkDeviceDict:
            network.setNetworkDevice(
                NetworkDevice.getFromDbDict(networkDeviceDict.__dict__))

        return network
