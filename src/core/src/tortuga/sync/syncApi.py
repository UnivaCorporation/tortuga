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

from tortuga.sync.syncManager import SyncManager
from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException


class SyncApi(TortugaApi):
    """Cluster sync API class"""

    def scheduleClusterUpdate(self, updateReason=None):
        """Schedule cluster update.

            Returns:
                None
            Throws:
                UserNotAuthorized
                TortugaException
        """
        try:
            SyncManager().scheduleClusterUpdate(updateReason)
        except Exception as ex:
            if isinstance(ex, TortugaException):
                raise

            self.getLogger().exception('Error scheduling cluster update')

            raise TortugaException(exception=ex)

    def getUpdateStatus(self):
        """Return cluster update status

            Returns:
                Boolean - True if cluster update is currently running
            Throws:
                TortugaException
        """
        try:
            return SyncManager().getUpdateStatus()
        except Exception as ex:
            if isinstance(ex, TortugaException):
                raise

            self.getLogger().exception('Error getting update status')

            raise TortugaException(exception=ex)
