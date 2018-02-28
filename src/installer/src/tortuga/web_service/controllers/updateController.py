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

import cherrypy

from tortuga.sync.syncApi import SyncApi
from .tortugaController import TortugaController
from .authController import AuthController, require


class UpdateController(TortugaController):
    """
    Update controller class.

    """
    actions = [
        {
            'name': 'clusterUpdate',
            'path': '/v1/updates/cluster',
            'action': 'scheduleClusterUpdateRequest',
            'method': ['POST', 'GET'],
        },
    ]

    def __init__(self):
        super(UpdateController, self).__init__()

        self._syncApi = SyncApi()

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def scheduleClusterUpdateRequest(self):
        # Could be post or get...
        if cherrypy.request.method == 'POST':
            return self.scheduleClusterUpdate()
        else:
            return self.getUpdateStatus()

    def scheduleClusterUpdate(self):
        """ Schedule cluster update. """

        response = None

        postdata = cherrypy.request.json

        updateReason = postdata['reason'] \
            if 'reason' in postdata else None

        try:
            self._syncApi.scheduleClusterUpdate(updateReason)
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    def getUpdateStatus(self):
        """ Get cluster update status. """

        try:
            status = self._syncApi.getUpdateStatus()

            response = {
                'running': status,
            }
        except Exception as ex:
            self.getLogger().error('%s' % ex)
            self.handleException(ex)
            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
