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

# pylint: disable=no-member,not-callable

import http.client

import cherrypy

from tortuga.db.resourceAdapterDbApi import ResourceAdapterDbApi
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.resourceAdapterNotFound import ResourceAdapterNotFound
from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.resourceAdapterConfiguration.api import \
    ResourceAdapterConfigurationApi
from tortuga.schema import ResourceAdapterConfigSchema
from tortuga.web_service.auth.decorators import authentication_required

from .tortugaController import TortugaController


class ResourceAdapterConfigurationController(TortugaController):
    """
    Resource adapter configuration WS API controller

    """
    actions = [
        {
            'name': 'get_resource_adapters',
            'path': '/v1/resourceadapters/',
            'action': 'get_resource_adapters',
            'method': ['GET'],
        },
        {
            'name': 'create_resource_adapter_configuration',
            'path': '/v1/resourceadapters/:(resadapter_name)/profile/:(name)',
            'action': 'create',
            'method': ['POST'],
        },
        {
            'name': 'get_resource_adapter_configuration',
            'path': '/v1/resourceadapters/:(resadapter_name)/profile/:(name)',
            'action': 'get',
            'method': ['GET'],
        },
        {
            'name': 'get_resource_adapter_configuration_profile_names',
            'path': '/v1/resourceadapters/:(resadapter_name)/profile/',
            'action': 'get_profile_names',
            'method': ['GET'],
        },
        {
            'name': 'update_resource_adapter_configuration',
            'path': '/v1/resourceadapters/:(resadapter_name)/profile/:(name)',
            'action': 'update',
            'method': ['PUT'],
        },
        {
            'name': 'delete_resource_adapter_configuration',
            'path': '/v1/resourceadapters/:(resadapter_name)/profile/:(name)',
            'action': 'delete',
            'method': ['DELETE'],
        },
    ]

    @cherrypy.tools.json_out()
    def get_resource_adapters(self):
        try:
            response = [
                adapter.getCleanDict()
                for adapter in
                ResourceAdapterDbApi().getResourceAdapterList()
            ]
        except Exception:  # noqa pylint: disable=broad-except
            # Unhandled server exception
            self.getLogger().exception('create() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def create(self, resadapter_name, name):
        postdata = cherrypy.request.json

        try:
            if not postdata or (postdata and 'configuration' not in postdata):
                raise InvalidArgument(
                    'Malformed arguments: missing \'configuration\' value')

            ResourceAdapterConfigurationApi().create(
                cherrypy.request.db, resadapter_name, name,
                postdata['configuration'])

            response = None
        except ResourceAlreadyExists as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc), code=self.getTortugaStatusCode(exc),
                http_status=http.client.CONFLICT)
        except ResourceAdapterNotFound as exc:
            self.handleException(exc)

            response = self.notFoundErrorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except TortugaException as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except Exception:
            # Unhandled server exception
            self.getLogger().exception('create() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def get(self, resadapter_name, name):
        try:
            adapter_cfg = ResourceAdapterConfigurationApi().get(
                cherrypy.request.db, resadapter_name, name)

            response = ResourceAdapterConfigSchema().dump(adapter_cfg).data
        except ResourceAdapterNotFound as exc:
            self.handleException(exc)

            response = self.notFoundErrorResponse(str(exc))
        except TortugaException as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except Exception:  # noqa pylint: disable=broad-except
            # Unhandled server exception
            self.getLogger().exception('get() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def get_profile_names(self, resadapter_name):
        try:
            response = ResourceAdapterConfigurationApi().get_profile_names(
                cherrypy.request.db, resadapter_name)
        except ResourceAdapterNotFound as exc:
            self.handleException(exc)

            response = self.notFoundErrorResponse(str(exc))
        except TortugaException as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except Exception:  # noqa pylint: disable=broad-except
            # Unhandled server exception
            self.getLogger().exception('get() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authentication_required()
    def update(self, resadapter_name, name):
        configuration = cherrypy.request.json

        try:
            ResourceAdapterConfigurationApi().update(
                cherrypy.request.db, resadapter_name, name, configuration)

            response = None
        except ResourceAdapterNotFound as exc:
            self.handleException(exc)

            response = self.notFoundErrorResponse(str(exc))
        except TortugaException as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except Exception:  # noqa pylint: disable=broad-except
            # Unhandled server exception
            self.getLogger().exception('update() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @authentication_required()
    def delete(self, resadapter_name, name):
        try:
            ResourceAdapterConfigurationApi().delete(
                cherrypy.request.db, resadapter_name, name)

            response = None
        except ResourceAdapterNotFound as exc:
            self.handleException(exc)

            response = self.notFoundErrorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except TortugaException as exc:
            self.handleException(exc)

            response = self.errorResponse(
                str(exc),
                code=self.getTortugaStatusCode(exc))
        except Exception:  # noqa pylint: disable=broad-except
            # Unhandled server exception
            self.getLogger().exception('delete() failed')

            response = self.errorResponse(
                'Internal server error',
                http_status=http.client.INTERNAL_SERVER_ERROR)

        return self.formatResponse(response)
