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


class Admin(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'admin'

    def __init__(self, username=None, password=None, realname=None,
                 description=None):
        TortugaObject.__init__(self, {
            'username': username,
            'password': password,
            'realname': realname or username,
            'description': description
        }, ['id'], Admin.ROOT_TAG)

    def setId(self, id_):
        """ Set admin id."""
        self['id'] = id_

    def getId(self):
        """ Return admin id. """
        return self.get('id')

    def setUsername(self, username):
        """ Set username."""
        self['username'] = username

    def getUsername(self):
        """ Return username. """
        return self.get('username')

    def setPassword(self, password):
        """ Set password."""
        self['password'] = password

    def getPassword(self):
        """ Return password. """
        return self.get('password')

    def setRealname(self, realname):
        """ Set real name """
        self['realname'] = realname

    def getRealname(self):
        """ Return real name """
        return self.get('realname')

    def setDescription(self, description):
        """ Set description """
        self['description'] = description

    def getDescription(self):
        """ Return description """
        return self.get('description')

    @staticmethod
    def getKeys():
        return ['id', 'username', 'password', 'realname', 'description']
