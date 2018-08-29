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

from tortuga.config.configManager import ConfigManager
from tortuga.node.nodeApi import NodeApi
from tortuga.admin.api import AdminApi
from tortuga.network.networkApi import NetworkApi
from tortuga.parameter.parameterApi import ParameterApi


class Application:
    def __init__(self):
        self._cm: ConfigManager = None
        self._node_api: NodeApi = None
        self._admin_api: AdminApi = None
        self._network_api: NetworkApi = None
        self._parameter_api: ParameterApi = None

    @property
    def cm(self):
        if not self._cm:
            self._cm = ConfigManager()
        return self._cm

    @property
    def node_api(self):
        if not self._node_api:
            self._node_api = NodeApi()
        return self._node_api

    @property
    def admin_api(self):
        if not self._admin_api:
            self._admin_api = AdminApi()
        return self._admin_api

    @property
    def network_api(self):
        if not self._network_api:
            self._network_api = NetworkApi()
        return self._network_api

    @property
    def parameter_api(self):
        if not self._parameter_api:
            self._parameter_api = ParameterApi()
        return self._parameter_api
