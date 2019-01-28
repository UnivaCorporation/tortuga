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

from typing import Optional

import cherrypy

from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.kit.manager import KitManager
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.web_service.auth.decorators import authentication_required

from .tortugaController import TortugaController


class KitController(TortugaController):
    """
    Admin kit controller class.

    """
    actions = [
        {
            'name': 'userKits',
            'path': '/v1/kits/',
            'action': 'kitsAction',
            'method': ['GET', 'DELETE']
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
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def kitEulaRequest(self, name, version):
        # Must be 'GET'
        return self.getKitEula(name, version)

    def getKit(self, name: str, version: Optional[str], iteration: Optional[str]):
        """
        Return info for the specified kit.

        Raises:
            KitNotFound
        """

        self._logger.debug(
            'getKit(): name=[%s], version=[%s], iteration=[%s]' % (
                name, version, iteration))

        return KitManager().getKit(
            cherrypy.request.db, name, version=version, iteration=iteration)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def getKitById(self, kit_id):
        """ Return info for the specified kit by id. """

        try:
            kit = KitManager().getKitById(cherrypy.request.db, kit_id)

            response = {
                'kit': kit.getCleanDict(),
            }
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def kitsAction(self, **kwargs):
        """
        Return list of all available kits.
        """

        response = None

        try:
            name = kwargs.get('name')
            version = kwargs.get('version')
            iteration = kwargs.get('iteration')

            if cherrypy.request.method == 'DELETE':
                KitManager().deleteKit(
                    cherrypy.request.db, name, version, iteration)
            else:
                # GET method
                if name:
                    # get kit by name
                    kitList = TortugaObjectList(
                        [self.getKit(name,
                                     version=version,
                                     iteration=iteration)]
                    )
                else:
                    # get all kits
                    kitList = KitManager().getKitList(cherrypy.request.db)

                response = {'kits': kitList.getCleanDict()}
        except KitNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def installKit(self, name, version, iteration=None):
        """ Install kit by name, version and iteration. """

        response = None

        try:
            KitManager().installKit(
                cherrypy.request.db, name, version, iteration, key)
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def getKitEula(self, name, version, iteration=None):
        """ Get kit Eula. """

        try:
            eula = KitManager().get_kit_eula(
                cherrypy.request.db, name, version, iteration)

            response = eula.getCleanDict()
        except Exception as ex:
            self._logger.error(str(ex))
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
