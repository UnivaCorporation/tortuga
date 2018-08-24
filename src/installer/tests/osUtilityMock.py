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

from sqlalchemy.orm.session import Session

from tortuga.config.configManager import ConfigManager
from tortuga.db.models.node import Node
from tortuga.node import state


class MockBootHostManager:
    def __init__(self, configManager: ConfigManager) -> None:
        pass

    def setNodeForNetworkBoot(self, session: Session, dbNode: Node): \
            # pylint: disable=unused-argument
        dbNode.state = state.NODE_STATE_EXPIRED

    def writePXEFile(self, *args, **kwargs): \
            # pylint: disable=unused-argument
        return

    def addDhcpLease(self, *args, **kwargs): \
            # pylint: disable=unused-argument
        pass


class MockOsObjectFactory:
    def getOsBootHostManager(self, configManager: ConfigManager): \
            # pylint: disable=unused-argument,no-self-use
        return MockBootHostManager(configManager)


def get_os_object_factory(osName: str = None): \
        # pylint: disable=unused-argument
    return MockOsObjectFactory()
