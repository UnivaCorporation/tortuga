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

# pylint: disable=no-name-in-module

import cherrypy
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.kit.manager import KitManager

from ..auth import authentication_required
from .tortugaController import TortugaController


class KitController(TortugaController):
    """
    Admin kit controller class.

    """
    actions = [
        {
            'name': 'userKits',
            'path': '/v1/kits/',
            'action': 'getKitList',
            'method': ['GET']
        },

        {
            'name': 'userKit',
            'path': '/v1/kits/:name/:version',
            'action': 'kitRequest',
            'method': ['GET']
        },
        {
            'name': 'userKitId',
            'path': '/v1/kits/:kit_id',
            'action': 'getKitById',
            'method': ['GET']
        },
        {
            'name': 'adminKit',
            'path': '/v1/kits/:(name)/:(version)/eula',
            'action': 'kitEulaRequest',
            'method': ['GET']
        },
        {
            'name': 'deleteKit',
            'path': '/v1/kits/:(name)/:(version)',
            'action': 'deleteKit',
            'method': ['DELETE'],
        }
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def kitRequest(self, name, version, key=None):
        # tmpVersion, iteration = version.rsplit('-', 1)

        vals = version.rsplit('-', 1)

        iteration = vals[1] if len(vals) == 2 else None

        version_ = vals[0]

        if cherrypy.request.method == 'POST':
            return self.installKit(name, version_, iteration, key)
        elif cherrypy.request.method == 'DELETE':
            return self.deleteKit(name, version_, iteration)
        else:
            # Must be 'GET'
            return self.getKit(name, version_, iteration)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def kitEulaRequest(self, name, version):
        # Must be 'GET'
        return self.getKitEula(name, version)

    def getKit(self, name, version, iteration=None):
        """ Return info for the specified kit. """

        self.getLogger().debug(
            '[%s] getKit(): name=[%s], version=[%s], iteration=[%s]' % (
                self.__module__, name, version, iteration))

        try:
            kit = KitManager().getKit(
                name, version, iteration)

            response = {'kit': kit.getCleanDict()}
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getKitById(self, kit_id):
        """ Return info for the specified kit by id. """

        try:
            kit = KitManager().getKitById(kit_id)

            response = {
                'kit': kit.getCleanDict(),
            }
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getKitList(self):
        """ Return list of all available kits. """

        try:
            kitList = KitManager().getKitList()

            response = {'kits': kitList.getCleanDict()}
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def installKit(self, name, version, iteration=None, key=None):
        """ Install kit by name, version and iteration. """

        response = None

        try:
            KitManager().installKit(
                name, version, iteration, key)
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def getKitEula(self, name, version, iteration=None):
        """ Get kit Eula. """

        try:
            eula = KitManager().get_kit_eula(
                name, version, iteration)

            response = eula.getCleanDict()
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def deleteKit(self, name: str, version: str) -> str:
        """
        Remove kit by name and version
        """

        response = None

        # 'version' can be formatted as '<version>-<iteration>'
        if '-' in version:
            version, iteration = version.split('-', 1)
        else:
            iteration = None

        try:
            KitManager().deleteKit(name, version, iteration)
        except KitNotFound:
            pass
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
