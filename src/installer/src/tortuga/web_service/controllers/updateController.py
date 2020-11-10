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
import json

from tortuga.types.application import Application
from tortuga.web_service.auth.decorators import authentication_required

from .tortugaController import TortugaController


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

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def scheduleClusterUpdateRequest(self):
        # Could be post or get...
        if cherrypy.request.method == 'POST':
            # POST handler
            return self.scheduleClusterUpdate()

        # GET handler
        return self.getUpdateStatus()

    def scheduleClusterUpdate(self): \
            # pylint: disable=broad-except
        """
        Schedule cluster update
        """

        response = None

        postdata = cherrypy.request.json

        updateReason = postdata['reason'] \
            if 'reason' in postdata else None

        opts = json.loads(postdata['opts']) \
            if 'opts' in postdata else {}

        # TODO - placeholder, need to handle cluster update here

        return self.formatResponse(response)

    def getUpdateStatus(self): \
            # pylint: disable=broad-except
        """
        Get cluster update status
        """
        # TODO - placeholder, need to provide a new way to get update status
        response = None

        return self.formatResponse(response)
