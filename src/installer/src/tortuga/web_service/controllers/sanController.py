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

# pylint: disable=no-member,no-name-in-module

import cherrypy

from tortuga.san.sanApi import SanApi
from tortuga.web_service.auth.decorators import authentication_required
from .tortugaController import TortugaController


class SanController(TortugaController):
    """
    Admin SAN controller class. DEPRECATED.

    """

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required
    def getVolumeList(self):
        """Return list of all available volumes"""

        # self._logger.debug('Retrieving volume list')

        try:
            volumeList = SanApi().getVolumeList()

            response = volumeList.getCleanDict()
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

            return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def addVolume(self, storageAdapter, size, nameFormat='*',
                  shared=False):
        """ Add volume to the SAN system"""

        # self._logger.debug('Adding volume')

        try:
            volume = SanApi().addVolume(
                storageAdapter, size, nameFormat, 'True' == shared)

            response = volume.getCleanDict()
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def updateVolume(self, volume, shared):
        """Update volume in SAN system"""

        response = None

        # self._logger.debug('Updating volume')

        try:
            SanApi().updateVolume(volume, shared == 'True')
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def deleteVolume(self, volume):
        """Delete Volume from SAN system"""

        response = None

        # self._logger.debug('Deleting volume')

        try:
            SanApi().deleteVolume(volume)
        except Exception as ex:
            self._logger.error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
