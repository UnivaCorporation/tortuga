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
from tortuga.db.instanceMetadataDbHandler import InstanceMetadataDbHandler
from tortuga.schema import InstanceMetadataSchema
from tortuga.web_service.auth.decorators import authentication_required

from .tortugaController import TortugaController


instanceMetadataDbHandler = InstanceMetadataDbHandler()


class MetadataController(TortugaController):
    """Metadata controller class."""

    actions = [
        {
            'name': 'listMetadata',
            'path': '/v1/metadata/',
            'action': 'list',
            'method': ['GET'],
        },
        {
            'name': 'deleteMetadata',
            'path': '/v1/metadata/',
            'action': 'delete',
            'method': ['DELETE'],
        },
    ]

    @cherrypy.tools.json_out()
    @authentication_required()
    def list(self, **kwargs):
        try:
            response = InstanceMetadataSchema().dump(
                instanceMetadataDbHandler.list(
                    cherrypy.request.db,
                    filter_key=kwargs.get('filter_key'),
                    filter_value=kwargs.get('filter_value'),
                ),
                many=True,
            ).data
        except Exception as exc:
            self.getLogger().exception('metadata GET exception')

            self.handleException(exc)

            response = self.errorResponse(str(exc))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def delete(self, **kwargs):
        try:
            instanceMetadataDbHandler.delete(
                cherrypy.request.db,
                filter_key=kwargs.get('filter_key'),
                filter_value=kwargs.get('filter_value'),
            )

            # commit delete request
            cherrypy.request.db.commit()

            response = None
        except Exception as exc:
            self.getLogger().exception('metadata DELETE exception')

            self.handleException(exc)

            response = self.errorResponse(str(exc))

        return self.formatResponse(response)
