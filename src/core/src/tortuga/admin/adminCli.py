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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest


class AdminCli(TortugaCli):
    """
    Base admin command line interface class.
    """

    def getAdminUsernameAndPassword(self):
        adminUsername = self._options.adminUsername
        adminPassword = self._options.adminPassword

        if not adminUsername:
            raise InvalidCliRequest(_('Missing Admin User Name.'))

        if not adminPassword:
            raise InvalidCliRequest(_('Missing Admin Password.'))

        return adminUsername, adminPassword
