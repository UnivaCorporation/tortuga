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

from tortuga.os_objects.osObjectManager import OsObjectManager
from tortuga.helper import osHelper


class DnsManager(OsObjectManager):
    """RHEL dns manager"""

    SERVICE_CONFIG_FILE = '/etc/named.conf'
    CONFIG_DIR = '/var/named'
    SERVICE_NAME = 'named'

    def __init__(self):
        OsObjectManager.__init__(self)

        self._osInfo = osHelper.getOsInfo()

    def getServiceConfigFile(self): \
            # pylint: disable=no-self-use
        """ Get configuration file"""

        return DnsManager.SERVICE_CONFIG_FILE

    def getConfigDir(self): \
            # pylint: disable=no-self-use
        """ Get configuration dir"""

        return DnsManager.CONFIG_DIR

    def getServiceName(self): \
            # pylint: disable=no-self-use
        """ Get service name"""

        return DnsManager.SERVICE_NAME
