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

import os

from tortuga.os_objects.osSqliteManagerInterface \
    import OsSqliteManagerInterface
from tortuga.os_objects.osObjectManager import OsObjectManager


class RhelSqliteManager(OsObjectManager, OsSqliteManagerInterface):
    """
    RHEL sqlite manager.
    """

    def __init__(self):
        OsObjectManager.__init__(self)

    def destroyDb(self, dbSchema):
        """
        Destroy DB.

            Returns:
                None
            Throws:
                CommandFailed
                TortugaException
        """

        dbpath = os.path.join(
            self._cm.getRoot(), 'etc', dbSchema + '.sqlite')

        if os.path.exists(dbpath):
            os.unlink(dbpath)
