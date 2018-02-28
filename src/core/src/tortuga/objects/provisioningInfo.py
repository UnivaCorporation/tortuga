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

from tortuga.objects.tortugaObject import TortugaObject

from tortuga.objects import node
from tortuga.objects import parameter


class ProvisioningInfo(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'provisioninginfo'

    def __init__(self):
        TortugaObject.__init__(self, {}, [], ProvisioningInfo.ROOT_TAG)

    def setNode(self, val):
        self['node'] = val

    def getNode(self):
        return self.get('node')

    def setGlobalParameters(self, val):
        self['globalparameters'] = val

    def getGlobalParameters(self):
        return self.get('globalparameters')

    def getGlobalParameter(self, name):
        """
        Iterate over global parameters and return the entry with the
        matching name
        """

        for entry in self.getGlobalParameters():
            if entry.getName() == name:
                return entry.getValue()

        return ''

    @classmethod
    def getFromDict(cls, dict_):
        """ Get provisioning info from dict. """

        provisioningInfo = super(ProvisioningInfo, cls).getFromDict(dict_)

        nodeDict = dict_.get(node.Node.ROOT_TAG)
        if nodeDict:
            provisioningInfo.setNode(node.Node.getFromDict(nodeDict))

        provisioningInfo.setGlobalParameters(
            parameter.Parameter.getListFromDict(dict_))

        return provisioningInfo
