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

from tortuga.objects import node
from tortuga.objects.tortugaObject import TortugaObject, TortugaObjectList
from tortuga.utility.helper import str2bool


class AddHostStatus(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'addhoststatus'

    def __init__(self):

        TortugaObject.__init__(self, {
            'nodes': TortugaObjectList(),
            'strings': TortugaObjectList(),
            'running': False
        }, [], AddHostStatus.ROOT_TAG)

    def setNodeList(self, val):
        self['nodes'] = val

    def getNodeList(self):
        return self.get('nodes')

    def setMessageList(self, val):
        self['strings'] = val

    def getMessageList(self):
        return self.get('strings')

    def setIsRunning(self, val):
        self['running'] = str2bool(val)

    def getIsRunning(self):
        return str2bool(self.get('running'))

    @staticmethod
    def getKeys():
        return ['running']

    @classmethod
    def getFromDict(cls, dict_):
        """ Get addHostStatus from dict. """

        addHostStatus = super(AddHostStatus, cls).getFromDict(dict_)

        addHostStatus.setNodeList(node.Node.getListFromDict(dict_))
        addHostStatus.setMessageList(
            dict_['strings'] if 'strings' in dict_ else [])

        return addHostStatus
