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

import cherrypy

from tortuga.db.tagsDbHandler import TagsDbHandler
from .. import dbm
from .authController import AuthController, require
from .tortugaController import TortugaController


class TagController(TortugaController):
    """
    CherryPy WS controller for managing resource tags

    """
    actions = [
        {
            'name': 'get_tags',
            'path': '/v1/tags/',
            'action': 'get',
            'method': ['GET'],
        },
        {
            'name': 'get_tags',
            'path': '/v1/tags/:(name)',
            'action': 'get',
            'method': ['GET'],
        },
        {
            'name': 'delete_tag',
            'path': '/v1/tags/:(name)',
            'action': 'delete',
            'method': ['DELETE'],
        },
    ]

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def get(self, name=None):
        try:
            if name is None:
                results = [dict(name=tag.name,
                                value=tag.value)
                            for tag in TagsDbHandler().get_tags(
                                cherrypy.request.db)]

                response = results
            else:
                tag = TagsDbHandler().get_tag(cherrypy.request.db, name)
                if tag:
                    # Tag found
                    response = dict(name=tag.name, value=tag.value)
                else:
                    response = self.notFoundErrorResponse(
                        'Tag {0} not found'.format(name))
        except Exception as ex:
            if name:
                errmsg = 'Error getting tag \'{0}\''.format(name)
            else:
                errmsg = 'Error getting tags'

            self.getLogger().exception(errmsg)

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @require()
    def delete(self, name):
        try:
            response = None

            TagsDbHandler().delete(cherrypy.request.db, name)

            # Yes, I know this should be buried in a lower-level API...
            cherrypy.request.db.commit()
        except Exception as ex:
            self.getLogger().exception(
                'Error deleting tag \'{0}\''.format(name))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
