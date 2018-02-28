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

from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter
from tortuga.db.nodes import Nodes
from tortuga.db.nics import Nics


class Generic(ResourceAdapter):
    __adaptername__ = 'generic'

    def start(self, addNodesRequest, dbSession, dbHardwareProfile,
              dbSoftwareProfile=None):

        nodes = []

        for node_detail in addNodesRequest['nodeDetails']:
            node = Nodes(name=node_detail['name'])
            node.hardwareprofile = dbHardwareProfile
            node.softwareprofile = dbSoftwareProfile

            node.nics = []

            for nic_detail in node_detail['nics']:

                nic = Nics()
                nic.ip = nic_detail['ip']

                print(node_detail)

            node.nics.append(nic)

            nodes.append(node)

        return nodes
