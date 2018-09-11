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

import tortuga.objects.admin
import tortuga.objects.module
import tortuga.objects.network
import tortuga.objects.networkDevice
import tortuga.objects.node
import tortuga.objects.resourceAdapter
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList
from tortuga.utility.helper import str2bool


class HardwareProfile(TortugaObject): \
        # pylint: disable=too-many-public-methods

    INST_TYPE_PACKAGE = 'package'
    INST_TYPE_IMAGED = 'imaged'
    INST_TYPE_IMAGED_UNMANAGED = 'imaged-unmanaged'

    ROOT_TAG = 'hardwareprofile'

    def __init__(self, name=None):
        TortugaObject.__init__(self, {
            'name': name,
            'networks': TortugaObjectList(),
            'admins': TortugaObjectList(),
            'nodes': TortugaObjectList(),
            'nics': TortugaObjectList(),
        }, ['name', 'id'], HardwareProfile.ROOT_TAG)

    def __repr__(self):
        return self.getName()

    def __hash__(self):
        return hash(str(self))

    def setName(self, name):
        """ Set hardware profile name."""
        self['name'] = name

    def getName(self):
        """ Return hardware profile name. """
        return self.get('name')

    def setId(self, id_):
        """ Set hardware profile id."""
        self['id'] = id_

    def getId(self):
        """ Return hardware profile id. """
        return self.get('id')

    def setInstallType(self, installType):
        """ Set install type."""
        self['installType'] = installType

    def getInstallType(self):
        """ Return install type. """
        return self.get('installType')

    def setDescription(self, description):
        """ Set description."""
        self['description'] = description

    def getDescription(self):
        """ Return description. """
        return self.get('description')

    def setNameFormat(self, nameFormat):
        """ Set name format."""
        self['nameFormat'] = nameFormat

    def getNameFormat(self):
        """ Return name format. """
        return self.get('nameFormat')

    def setKernel(self, kernel):
        """ Set kernel."""
        self['kernel'] = kernel

    def getKernel(self):
        """ Return kernel. """
        return self.get('kernel')

    def setInitrd(self, initrd):
        """ Set initrd."""
        self['initrd'] = initrd

    def getInitrd(self):
        """ Return initird. """
        return self.get('initrd')

    def setKernelParams(self, kernelParams):
        """ Set kernel params."""
        self['kernelParams'] = kernelParams

    def getKernelParams(self):
        """ Return kernel params. """
        return self.get('kernelParams')

    def setCost(self, cost):
        """ Set cost."""
        self['cost'] = cost

    def getCost(self):
        """ Return cost. """
        return self.get('cost')

    def setNetworks(self, networks):
        """ Set networks info. """
        self['networks'] = networks

    def getNetworks(self):
        """ Get networks. """
        return self.get('networks')

    def setAdmins(self, admins):
        """ Set admins info. """
        self['admins'] = admins

    def getAdmins(self):
        """ Get admins. """
        return self.get('admins')

    def setNodes(self, val):
        self['nodes'] = val

    def getNodes(self):
        return self.get('nodes')

    def setSoftwareOverrideAllowed(self, allowed):
        """ Set hardware profile override allowed flag."""
        self['softwareOverrideAllowed'] = str2bool(allowed)

    def getSoftwareOverrideAllowed(self):
        """ Return hardware profile override allowed flag. """
        return str2bool(self.get('softwareOverrideAllowed'))

    def setIdleSoftwareProfileId(self, swId):
        """ Set idle software profile ID. """
        self['idleSoftwareProfileId'] = swId

    def getIdleSoftwareProfileId(self):
        """ Return idle software profile ID. """
        return self.get('idleSoftwareProfileId')

    def setIdleSoftwareProfile(self, idleSoftwareProfile):
        self['idleSoftwareProfile'] = idleSoftwareProfile

    def getIdleSoftwareProfile(self):
        return self.get('idleSoftwareProfile')

    def setLocation(self, location):
        """ Set location. """
        self['location'] = location

    def getLocation(self):
        """ Return location. """
        return self.get('location')

    def setLocalBootParams(self, localBootParams):
        """ Set local boot params. """
        self['localBootParams'] = localBootParams

    def getLocalBootParams(self):
        """ Return local boot params. """
        return self.get('localBootParams')

    def setResourceAdapter(self, resourceAdapter):
        """ Set resource adapter. """
        self['resourceadapter'] = resourceAdapter

    def getResourceAdapter(self):
        """ Return resource adapter. """
        return self.get('resourceadapter')

    def setDefaultResourceAdapterConfig(self, value):
        self['default_resource_adapter_config'] = value

    def getDefaultResourceAdapterConfig(self):
        return self.get('default_resource_adapter_config')

    def getProvisioningNetwork(self):
        '''
        A hardware profile may have multiple networks that are marked as
        "provisioning".  However, that really means "private", and only
        one of them is used for actual provisioning. This figures out
        which one.
        '''

        best = None

        for network in self.getNetworks():
            if network.isProvisioning():
                if best is None or network.getNetworkDevice().getName() < \
                        best.getNetworkDevice().getName():
                    best = network

        if best is None:
            raise ConfigurationError(
                "Can't getProvisioningNetwork for ng %s" % (
                    self.getName()))

        return best

    #

    def setProvisioningNics(self, nics):
        """ set ProvisioningNics """
        self['nics'] = nics

    def getProvisioningNics(self):
        """ Get Provisioning Nics """
        return self.get('nics')

    def getTags(self):
        return self.get('tags')

    def setTags(self, value):
        self['tags'] = value

    @staticmethod
    def getKeys():
        return [
            'id',
            'name',
            'description',
            'nameFormat',
            'installType',
            'kernel',
            'kernelParams',
            'initrd',
            'softwareOverrideAllowed',
            'idleSoftwareProfileId',
            'location',
            'localBootParams',
            'cost',
            'default_resource_adapter_config',
            'tags',
        ]

    @classmethod
    def getFromDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        hardwareProfile = super(HardwareProfile, cls).getFromDict(_dict)

        hardwareProfile.setAdmins(
            tortuga.objects.admin.Admin.getListFromDict(_dict))

        hardwareProfile.setNodes(
            tortuga.objects.node.Node.getListFromDict(_dict))

        hardwareProfile.setProvisioningNics(
            tortuga.objects.nic.Nic.getListFromDict(_dict))

        resourceAdapterDict = _dict.get(
            tortuga.objects.resourceAdapter.ResourceAdapter.ROOT_TAG)

        if resourceAdapterDict:
            hardwareProfile.setResourceAdapter(
                tortuga.objects.resourceAdapter.ResourceAdapter.getFromDict(
                    resourceAdapterDict))

        hardwareProfile.setNetworks(
            tortuga.objects.network.Network.getListFromDict(_dict))

        # Sanity checking... do not allow the parsed XML to build an
        # invalid list of locations.
        if 'locations' in _dict:
            raise ConfigurationError(
                'Hardware profile can have only one location defined')

        return hardwareProfile

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        hardwareProfile = super(HardwareProfile, cls).getFromDict(
            _dict, ignore=ignore)

        hardwareProfile.setAdmins(
            tortuga.objects.admin.Admin.getListFromDbDict(_dict))

        if ignore and 'nodes' not in ignore:
            hardwareProfile.setNodes(
                tortuga.objects.node.Node.getListFromDbDict(_dict))

        hardwareProfile.setProvisioningNics(
            tortuga.objects.nic.Nic.getListFromDbDict(_dict))

        resourceAdapterDict = _dict.get(
            tortuga.objects.resourceAdapter.ResourceAdapter.ROOT_TAG)

        if resourceAdapterDict:
            hardwareProfile.setResourceAdapter(
                tortuga.objects.resourceAdapter.ResourceAdapter.getFromDict(
                    resourceAdapterDict.__dict__))

        defaultResourceAdapterConfig = _dict.get(
            'default_resource_adapter_config'
        )

        if defaultResourceAdapterConfig:
            hardwareProfile.setDefaultResourceAdapterConfig(
                defaultResourceAdapterConfig.name
            )

        if _dict.get('idlesoftwareprofile'):
            hardwareProfile.setIdleSoftwareProfile(
                tortuga.objects.softwareProfile.SoftwareProfile.getFromDbDict(
                    _dict.get('idlesoftwareprofile').__dict__))

        # hardwareprofilenetworks (relation)
        hardwareProfileNetworks = _dict.get('hardwareprofilenetworks')

        if hardwareProfileNetworks:
            networkList = TortugaObjectList()

            for item in hardwareProfileNetworks:
                networkDict = item.network.__dict__
                networkDeviceDict = item.networkdevice.__dict__

                network = tortuga.objects.network.Network.getFromDbDict(
                    networkDict)

                networkdevice = tortuga.objects.networkDevice.\
                    NetworkDevice.getFromDbDict(networkDeviceDict)

                network.setNetworkDevice(networkdevice)

                networkList.append(network)

            hardwareProfile.setNetworks(networkList)

        if 'tags' in _dict:
            tags = {}

            for tag in _dict['tags']:
                tags[tag.name] = tag.value

            hardwareProfile.setTags(tags)

        return hardwareProfile
