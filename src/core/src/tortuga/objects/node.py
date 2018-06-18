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

import tortuga.objects.hardwareProfile
import tortuga.objects.nic
import tortuga.objects.softwareProfile
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList


class Node(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'node'

    def __init__(self, name=None):
        super(Node, self).__init__(
            {
                'name': name,
                'nics': TortugaObjectList(),
            }, ['name', 'id'], Node.ROOT_TAG)

    # Table columns in order as defined in the schema - please maintain
    # order.

    def __repr__(self):
        return '%s' % (self.getName())

    def setId(self, id_):
        """ Set node id."""
        self['id'] = id_

    def getId(self):
        """ Return node id. """
        return self.get('id')

    def setName(self, name):
        """ Set node name."""
        self['name'] = name

    def getName(self):
        """ Return node name. """
        return self.get('name')

    def setState(self, state):
        """ Set state."""
        self['state'] = state

    def getState(self):
        """ Return state. """
        return self.get('state')

    def setBootFrom(self, bootFrom):
        """ Set bootFrom tag."""
        self['bootFrom'] = int(bootFrom)

    def getBootFrom(self):
        """ Return bootFrom tag. """
        return self.get('bootFrom')

    def setLastUpdate(self, lastUpdate):
        """ Set last update."""
        self['lastUpdate'] = lastUpdate

    def getLastUpdate(self):
        """ Return last update. """
        return self.get('lastUpdate')

    def setRack(self, rack):
        """ Set rack."""
        self['rack'] = rack

    def getRack(self):
        """ Return rack. """
        return self.get('rack')

    def setRank(self, rank):
        """ Set rank."""
        self['rank'] = rank

    def getRank(self):
        """ Return rank. """
        return self.get('rank')

    def setLockedState(self, val):
        self['lockedState'] = val

    def getLockedState(self):
        return self.get('lockedState')

    def setIsIdle(self, val):
        self['isIdle'] = val

    def getIsIdle(self):
        return self.get('isIdle')

    def setDestSPId(self, val):
        self['destSPId'] = val

    def getDestSPId(self):
        return self.get('destSPId')

    def setAddHostSession(self, session):
        self['addHostSession'] = session

    def getAddHostSession(self):
        return self.get('addHostSession')

    # Other (non-column) attributes

    def setNics(self, nics):
        self['nics'] = nics

    def getNics(self):
        return self.get('nics')

    def setHardwareProfile(self, hardwareProfile):
        self['hardwareprofile'] = hardwareProfile

    def getHardwareProfile(self):
        return self.get('hardwareprofile')

    def setSoftwareProfile(self, softwareProfile):
        self['softwareprofile'] = softwareProfile

    def getSoftwareProfile(self):
        return self.get('softwareprofile')

    def setResourceAdapter(self, resource_adapter):
        self['resource_adapter'] = resource_adapter

    def getResourceAdapter(self):
        return self.get('resource_adapter')

    def getTags(self):
        return self.get('tags') or {}

    def setTags(self, tags):
        self['tags'] = tags

    def getVcpus(self):
        return self['vcpus']

    def setVcpus(self, vcpus):
        self['vcpus'] = int(vcpus)

    def getInstance(self):
        return self['instance']

    def setInstance(self, value):
        self['instance'] = value

    @staticmethod
    def getKeys():
        return [
            'id', 'name', 'state', 'bootFrom', 'lastUpdate',
            'rack', 'rank', 'hardwareProfileId', 'softwareProfileId',
            'lockedState', 'isIdle', 'destSPId', 'addHostSession',
            'resource_adapter', 'vcpus',
            'instance',
        ]

    @classmethod
    def getFromDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        """ Get node from _dict. """

        node = super(Node, cls).getFromDict(_dict)

        node.setNics(tortuga.objects.nic.Nic.getListFromDict(_dict))

        hardwareProfileDict = _dict.get(
            tortuga.objects.hardwareProfile.HardwareProfile.ROOT_TAG)

        if hardwareProfileDict:
            node.setHardwareProfile(
                tortuga.objects.hardwareProfile.HardwareProfile.
                getFromDict(hardwareProfileDict))

        softwareProfileDict = _dict.get(
            tortuga.objects.softwareProfile.SoftwareProfile.ROOT_TAG)

        if softwareProfileDict:
            node.setSoftwareProfile(
                tortuga.objects.softwareProfile.SoftwareProfile.
                getFromDict(softwareProfileDict))

        return node

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        node = super(Node, cls).getFromDict(_dict, ignore=ignore)

        # nics (relation)
        node.setNics(tortuga.objects.nic.Nic.getListFromDbDict(_dict))

        # hardwareprofile (relation)
        hardwareProfileDict = _dict.get(
            tortuga.objects.hardwareProfile.HardwareProfile.ROOT_TAG)

        if hardwareProfileDict:
            node.setHardwareProfile(
                tortuga.objects.hardwareProfile.HardwareProfile.
                getFromDbDict(hardwareProfileDict.__dict__))

            if hardwareProfileDict.resourceadapter:
                node.setResourceAdapter(
                    hardwareProfileDict.resourceadapter.name)

        # softwareprofile (relation)
        if (ignore and 'softwareprofile' not in ignore) or not ignore:
            softwareProfileDict = _dict.get(
                tortuga.objects.softwareProfile.SoftwareProfile.ROOT_TAG)

            if softwareProfileDict:
                node.setSoftwareProfile(
                    tortuga.objects.softwareProfile.SoftwareProfile.
                    getFromDbDict(softwareProfileDict.__dict__))

        tags = dict()

        if 'tags' in _dict and _dict['tags']:
            for tag in _dict['tags']:
                tags[tag.name] = tag.value

        node.setTags(tags)

        # instance mapping
        instance_mapping_dict = _dict.get('instance')
        if instance_mapping_dict:
            from tortuga.schema import InstanceMappingSchema

            node.setInstance(
                InstanceMappingSchema(
                    exclude=('node',
                             'resource_adapter_configuration.settings')
                ).dump(instance_mapping_dict).data)

        return node
