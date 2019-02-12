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

from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi
from tortuga.softwareprofile.softwareProfileManager import \
    SoftwareProfileManager
from tortuga.types.application import Application
from tortuga.web_service.auth.decorators import authentication_required

from .common import make_options_from_query_string, parse_tag_query_string
from .tortugaController import TortugaController


class SoftwareProfileController(TortugaController):
    actions = [
        {
            'name': 'getSoftwareProfiles',
            'path': '/v1/softwareprofiles/',
            'action': 'getSoftwareProfiles',
            'method': ['GET'],
        },
        {
            'name': 'getSoftwareProfileById',
            'path': '/v1/softwareprofiles/:(swprofile_id)',
            'action': 'getSoftwareProfileById',
            'method': ['GET'],
        },
        {
            'name': 'deleteSoftwareProfile',
            'path': '/v1/softwareprofiles/:(softwareProfileName)',
            'action': 'deleteSoftwareProfile',
            'method': ['DELETE'],
        },
        {
            'name': 'createSoftwareProfile',
            'path': '/v1/softwareprofiles/',
            'action': 'createSoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'copySoftwareProfile',
            'path': '/v1/softwareprofiles/:(srcSoftwareProfileName)/copy/:(dstSoftwareProfileName)',
            'action': 'copySoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'getUsableNodes',
            'path': '/v1/softwareprofiles/:(softwareProfileName)/usable',
            'action': 'getUsableNodes',
            'method': ['GET'],
        },
        {
            'name': 'updateSoftwareProfile',
            'path': '/v1/softwareprofiles/:(softwareProfileId)',
            'action': 'updateSoftwareProfile',
            'method': ['PUT'],
        },
        {
            'name': 'getSoftwareProfileProvisioningInfo',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/provisioningInfo',
            'action': 'getProvisioningInfo',
            'method': ['GET'],
        },
        {
            'name': 'getSoftwareProfileAdmins',
            'path': '/v1/softwareprofiles/:(softwareProfileName)/admins',
            'action': 'getAdmins',
            'method': ['GET'],
        },
        {
            'name': 'getEnabledComponents',
            'path': '/v1/softwareprofiles/:(softwareProfileName)/components',
            'action': 'getEnabledComponents',
            'method': ['GET'],
        },
        {
            'name': 'addSwAdmin',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/admin/:(adminUsername)',
            'action': 'addAdmin',
            'method': ['POST'],
        },
        {
            'name': 'deleteSwAdmin',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/admin/:(adminUsername)',
            'action': 'deleteAdmin',
            'method': ['DELETE'],
        },
        {
            'name': 'enableComponent',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/enable_components',
            'action': 'enableComponent',
            'method': ['PUT'],
        },
        {
            'name': 'disableComponent',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/disable_components',
            'action': 'disableComponent',
            'method': ['PUT'],
        },
        {
            'name': 'addUsableHardwareProfileToSoftwareProfile',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/mappings/:(hardwareProfileName)',
            'action': 'addUsableHardwareProfileToSoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'deleteUsableHardwareProfileFromSoftwareProfile',
            'path': '/v1/softwareprofiles/:(softwareProfileName)'
                    '/mappings/:(hardwareProfileName)',
            'action': 'deleteUsableHardwareProfileFromSoftwareProfile',
            'method': ['DELETE'],
        },
        {
            'name': 'softwareProfileNodes',
            'path': '/v1/softwareprofiles/:(softwareProfileName)/nodes',
            'action': 'getNodes',
            'method': ['GET'],
        },
    ]

    def __init__(self, app: Application) -> None:
        super().__init__(app)

        self._softwareProfileManager = SoftwareProfileManager()

    @authentication_required()
    @cherrypy.tools.json_out()
    def getSoftwareProfiles(self, **kwargs):
        """
        TODO: implement support for optionDict through query string
        """

        try:
            tagspec = []

            if 'tag' in kwargs and kwargs['tag']:
                tagspec.extend(parse_tag_query_string(kwargs['tag']))

            if 'name' in kwargs and kwargs['name']:
                default_options = [
                    'components',
                    'partitions',
                    'hardwareprofiles',
                    'tags',
                ]

                options = make_options_from_query_string(
                    kwargs['include']
                    if 'include' in kwargs else None,
                    default_options)

                softwareProfiles = TortugaObjectList(
                    [self._softwareProfileManager.getSoftwareProfile(
                        cherrypy.request.db,
                        kwargs['name'], optionDict=options)])
            else:
                softwareProfiles = \
                    self._softwareProfileManager.getSoftwareProfileList(
                        cherrypy.request.db, tags=tagspec)

            response = {
                'softwareprofiles': softwareProfiles.getCleanDict(),
            }
        except Exception as ex:
            self.handleException(ex)

            http_status = 404 \
                if isinstance(ex, SoftwareProfileNotFound) else 400

            response = self.errorResponse(str(ex), http_status=http_status)

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createSoftwareProfile(self):
        """Create software profile"""

        response = None

        postdata = cherrypy.request.json

        if 'softwareProfile' not in postdata:
            raise Exception('Malformed request')

        settingsDict = postdata['settingsDict'] \
            if 'settingsDict' in postdata else {}

        self._logger.debug(
            '[%s] createSoftwareProfile(): softwareProfile=[%s]' % (
                self.__module__, postdata['softwareProfile']))

        swProfileSpec = SoftwareProfile.getFromDict(
            postdata['softwareProfile'])

        try:
            swProfileSpec.validate()
            SoftwareProfileApi().createSoftwareProfile(
                cherrypy.request.db,
                swProfileSpec, settingsDict=settingsDict)

        except Exception as ex:
            self._logger.exception(
                'software profile WS API createSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteSoftwareProfile(self, softwareProfileName):
        """Delete software profile"""

        response = None

        # self._logger.debug('deleteSoftwareProfile()')

        try:
            SoftwareProfileApi().deleteSoftwareProfile(
                cherrypy.request.db, softwareProfileName)
        except SoftwareProfileNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API deleteSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def getSoftwareProfileById(self, swprofile_id, **kwargs):
        """
        Get software profile by name

        TODO: implement support for optionDict through query string
        """
        optionDict = {
            'admins': True,
            'components': True,
            'nodes': True,
            'os': True,
            'partitions': True,
        }

        try:
            sp = self._softwareProfileManager.getSoftwareProfileById(
                cherrypy.request.db, swprofile_id, optionDict)

            response = {
                'softwareprofile': sp.getCleanDict(),
            }
        except SoftwareProfileNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API getSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def updateSoftwareProfile(self, softwareProfileId):
        '''
        Handle put to softwareprofiles/:(softwareProfileId)
        '''

        response = None

        try:
            postdata = cherrypy.request.json

            swProfile = SoftwareProfile.getFromDict(postdata)

            # Make sure the id is synced
            swProfile.setId(softwareProfileId)

            self._softwareProfileManager.updateSoftwareProfile(
                cherrypy.request.db, swProfile)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API updateSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getEnabledComponents(self, softwareProfileName):
        """ Return list of all enabled components. """

        # self._logger.debug(
        #     'Retrieving enabled component list for [%s]' % (
        #         softwareProfileName))

        try:
            componentList = \
                self._softwareProfileManager.getEnabledComponentList(
                    cherrypy.request.db, softwareProfileName)

            response = {'components': componentList.getCleanDict()}
        except Exception as ex:
            self._logger.exception(
                'software profile WS API getEnabledComponents() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    def addUsableHardwareProfileToSoftwareProfile(self,
                                                  softwareProfileName,
                                                  hardwareProfileName):
        """
        Add hardware profile to software profile
        """

        response = None

        try:
            self._softwareProfileManager.addUsableHardwareProfileToSoftwareProfile(
                cherrypy.request.db, hardwareProfileName, softwareProfileName)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API'
                ' addUsableHardwareProfileToSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                       softwareProfileName,
                                                       hardwareProfileName):
        """ Delete hardware profile from software profile. """

        response = None

        try:
            self._softwareProfileManager.deleteUsableHardwareProfileFromSoftwareProfile(
                cherrypy.request.db, hardwareProfileName, softwareProfileName)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API'
                ' deleteUsableHardwareProfileFromSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addAdmin(self, softwareProfileName, adminUsername):
        response = None

        try:
            self._softwareProfileManager.addAdmin(
                cherrypy.request.db, softwareProfileName, adminUsername)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API addAdmin() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteAdmin(self, softwareProfileName, adminUsername):
        try:
            self._softwareProfileManager.deleteAdmin(
                cherrypy.request.db, softwareProfileName, adminUsername)

            response = None
        except Exception as ex:
            self._logger.exception(
                'software profile WS API deleteAdmin() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def enableComponent(self, softwareProfileName):
        response = None

        try:
            postdata = cherrypy.request.json

            if 'components' not in postdata or not postdata['components']:
                raise InvalidArgument('Malformed enable component request')

            # Reserved for possible future use where it will be possible to
            # enable multiple components in one request.
            component = postdata['components'][0]

            kitName = component['kitName']
            kitVersion = component['kitVersion']
            kitIteration = component['kitIteration']
            componentName = component['componentName']
            componentVersion = component['componentVersion']

            self._softwareProfileManager.enableComponent(
                cherrypy.request.db, softwareProfileName, kitName,
                kitVersion, kitIteration, componentName,
                comp_version=componentVersion,
            )
        except Exception as ex:
            self._logger.exception(
                'software profile WS API enableComponent() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def disableComponent(self, softwareProfileName):
        response = None

        try:
            postdata = cherrypy.request.json

            if 'components' not in postdata or not postdata['components']:
                raise InvalidArgument('Malformed disable component request')

            # Reserved for possible future use where it will be possible to
            # disable multiple components in one request.
            component = postdata['components'][0]

            kitName = component['kitName']
            kitVersion = component['kitVersion']
            kitIteration = component['kitIteration']
            componentName = component['componentName']
            componentVersion = component['componentVersion']

            self._softwareProfileManager.disableComponent(
                cherrypy.request.db, softwareProfileName, kitName,
                kitVersion, kitIteration, componentName, componentVersion,
            )
        except Exception as ex:
            self._logger.exception(
                'software profile WS API disableComponent() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        response = None

        try:
            self._softwareProfileManager.copySoftwareProfile(
                cherrypy.request.db, srcSoftwareProfileName,
                dstSoftwareProfileName)
        except Exception as ex:
            self._logger.exception(
                'software profile WS API copySoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getUsableNodes(self, softwareProfileName):
        try:
            nodeList = self._softwareProfileManager.getUsableNodes(
                cherrypy.request.db, softwareProfileName)

            response = {'nodes': nodeList.getCleanDict()}
        except Exception as ex:
            self._logger.exception(
                'software profile WS API getUsableNodes() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @authentication_required()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getNodes(self, softwareProfileName):
        try:
            nodeList = self._softwareProfileManager.getNodeList(
                cherrypy.request.db, softwareProfileName)

            response = {
                'nodes': nodeList,
            }
        except Exception as ex:
            self._logger.exception(
                'software profile WS API getNodes() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
