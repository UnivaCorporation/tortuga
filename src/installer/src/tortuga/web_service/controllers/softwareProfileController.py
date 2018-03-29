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

from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.softwareProfileNotFound import SoftwareProfileNotFound
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.schema import SoftwareProfileSchema
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi
from tortuga.softwareprofile.softwareProfileManager import \
    SoftwareProfileManager

from .authController import AuthController, require
from .common import parse_tag_query_string
from .tortugaController import TortugaController


class SoftwareProfileController(TortugaController):
    actions = [
        {
            'name': 'getSoftwareProfiles',
            'path': '/v1/softwareProfiles',
            'action': 'getSoftwareProfiles',
            'method': ['GET'],
        },
        {
            'name': 'deleteSoftwareProfile',
            'path': '/v1/softwareProfiles/:(softwareProfileName)',
            'action': 'deleteSoftwareProfile',
            'method': ['DELETE'],
        },
        {
            'name': 'createSoftwareProfile',
            'path': '/v1/softwareProfiles',
            'action': 'createSoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'copySoftwareProfile',
            'path': '/v1/softwareProfiles/:(srcSoftwareProfileName)/copy',
            'action': 'copySoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'getUsableNodes',
            'path': '/v1/softwareProfiles/:(softwareProfileName)/usable',
            'action': 'getUsableNodes',
            'method': ['GET'],
        },
        {
            'name': 'getIdleSoftwareProfiles',
            'path': '/v1/idleSoftwareProfiles',
            'action': 'getIdleSoftwareProfiles',
            'method': ['GET'],
        },
        {
            'name': 'updateSoftwareProfile',
            'path': '/v1/softwareProfiles/:(softwareProfileId)',
            'action': 'updateSoftwareProfile',
            'method': ['PUT'],
        },
        {
            'name': 'getSoftwareProfile',
            'path': '/v1/softwareProfiles/:(softwareProfileName)',
            'action': 'getSoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'getSoftwareProfileById',
            'path': '/v1/softwareProfiles/id/:(id)',
            'action': 'getSoftwareProfileById',
            'method': ['GET'],
        },
        {
            'name': 'getSoftwareProfileProvisioningInfo',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/provisioningInfo',
            'action': 'getProvisioningInfo',
            'method': ['GET'],
        },
        {
            'name': 'getSoftwareProfileAdmins',
            'path': '/v1/softwareProfiles/:(softwareProfileName)/admins',
            'action': 'getAdmins',
            'method': ['GET'],
        },
        {
            'name': 'getEnabledComponents',
            'path': '/v1/softwareProfiles/:(softwareProfileName)/components',
            'action': 'getEnabledComponents',
            'method': ['GET'],
        },
        {
            'name': 'addSwAdmin',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/admin/:(adminUsername)',
            'action': 'addAdmin',
            'method': ['POST'],
        },
        {
            'name': 'deleteSwAdmin',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/admin/:(adminUsername)',
            'action': 'deleteAdmin',
            'method': ['DELETE'],
        },
        {
            'name': 'enableComponent',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/enable_components',
            'action': 'enableComponent',
            'method': ['PUT'],
        },
        {
            'name': 'disableComponent',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/disable_components',
            'action': 'disableComponent',
            'method': ['PUT'],
        },
        {
            'name': 'addUsableHardwareProfileToSoftwareProfile',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/mappings/:(hardwareProfileName)',
            'action': 'addUsableHardwareProfileToSoftwareProfile',
            'method': ['POST'],
        },
        {
            'name': 'deleteUsableHardwareProfileFromSoftwareProfile',
            'path': '/v1/softwareProfiles/:(softwareProfileName)'
                    '/mappings/:(hardwareProfileName)',
            'action': 'deleteUsableHardwareProfileFromSoftwareProfile',
            'method': ['DELETE'],
        },
        {
            'name': 'softwareProfileNodes',
            'path': '/v1/softwareProfiles/:(softwareProfileName)/nodes',
            'action': 'getNodes',
            'method': ['GET'],
        },
    ]

    def __init__(self):
        TortugaController.__init__(self)

        self._softwareProfileManager = SoftwareProfileManager()

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getSoftwareProfiles(self, **kwargs):
        tagspec = []

        if 'tag' in kwargs and kwargs['tag']:
            tagspec.extend(parse_tag_query_string(kwargs['tag']))

        result = SoftwareProfilesDbHandler().getSoftwareProfileList(
            cherrypy.request.db, tags=tagspec
        )

        response = {
            'softwareprofiles': SoftwareProfileSchema().dump(
                result, many=True).data
        }

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getIdleSoftwareProfiles(self):
        idleSoftwareProfiles = self._softwareProfileManager.\
            getIdleSoftwareProfileList()

        response = {
            'softwareprofiles': idleSoftwareProfiles.getCleanDict(),
        }

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getSoftwareProfileById(self, id_):
        """Get software profile by id"""

        # self.getLogger().debug('getSoftwareProfileById(id=[%s])' % (id))

        try:
            sp = self._softwareProfileManager.getSoftwareProfileById(
                id_, {
                    'admins': True,
                    'components': True,
                    'nodes': True,
                    'os': True,
                    'packages': True,
                    'partitions': True,
                })

            response = {'softwareprofile': sp.getCleanDict()}
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API getSoftwareProfileById() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
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

        self.getLogger().debug(
            '[%s] createSoftwareProfile(): softwareProfile=[%s]' % (
                self.__module__, postdata['softwareProfile']))

        swProfileSpec = SoftwareProfile.getFromDict(
            postdata['softwareProfile'])

        try:
            SoftwareProfileApi().createSoftwareProfile(
                swProfileSpec, settingsDict=settingsDict)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API createSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteSoftwareProfile(self, softwareProfileName):
        """Delete software profile"""

        response = None

        # self.getLogger().debug('deleteSoftwareProfile()')

        try:
            SoftwareProfileApi().deleteSoftwareProfile(softwareProfileName)
        except SoftwareProfileNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API deleteSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getSoftwareProfile(self, softwareProfileName):
        """Get software profile by name"""

        postdata = cherrypy.request.json

        optionDict = postdata['optionDict'] \
            if 'optionDict' in postdata else {}

        try:
            sp = self._softwareProfileManager.getSoftwareProfile(
                softwareProfileName, optionDict)

            response = {
                'softwareprofile': sp.getCleanDict(),
            }
        except SoftwareProfileNotFound as ex:
            self.handleException(ex)
            code = self.getTortugaStatusCode(ex)
            response = self.notFoundErrorResponse(str(ex), code)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API getSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
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

            self._softwareProfileManager.updateSoftwareProfile(swProfile)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API updateSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getEnabledComponents(self, softwareProfileName):
        """ Return list of all enabled components. """

        # self.getLogger().debug(
        #     'Retrieving enabled component list for [%s]' % (
        #         softwareProfileName))

        try:
            componentList = self._softwareProfileManager.\
                getEnabledComponentList(softwareProfileName)

            response = {'components': componentList.getCleanDict()}
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API getEnabledComponents() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addUsableHardwareProfileToSoftwareProfile(self,
                                                  softwareProfileName,
                                                  hardwareProfileName):
        """ Add hardware profile to software profile. """

        # self.getLogger().debug(
        #     'Adding hardware profile [%s] to software profile [%s]' % (
        #         hardwareProfileName, softwareProfileName))

        response = None

        try:
            self._softwareProfileManager.\
                addUsableHardwareProfileToSoftwareProfile(
                    hardwareProfileName, softwareProfileName)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API'
                ' addUsableHardwareProfileToSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteUsableHardwareProfileFromSoftwareProfile(self,
                                                       softwareProfileName,
                                                       hardwareProfileName):
        """ Delete hardware profile from software profile. """

        response = None

        try:
            self._softwareProfileManager.\
                deleteUsableHardwareProfileFromSoftwareProfile(
                    hardwareProfileName, softwareProfileName)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API'
                ' deleteUsableHardwareProfileFromSoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addAdmin(self, softwareProfileName, adminUsername):
        response = None

        try:
            self._softwareProfileManager.addAdmin(
                softwareProfileName, adminUsername)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API addAdmin() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteAdmin(self, softwareProfileName, adminUsername):
        try:
            self._softwareProfileManager.deleteAdmin(
                softwareProfileName, adminUsername)

            response = None
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API deleteAdmin() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
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
                softwareProfileName, kitName, kitVersion, kitIteration,
                componentName, comp_version=componentVersion)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API enableComponent() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
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
                softwareProfileName, kitName, kitVersion, kitIteration,
                componentName, componentVersion)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API disableComponent() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        response = None

        try:
            self._softwareProfileManager.copySoftwareProfile(
                srcSoftwareProfileName, dstSoftwareProfileName)
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API copySoftwareProfile() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getUsableNodes(self, softwareProfileName):
        try:
            nodeList = self._softwareProfileManager.getUsableNodes(
                softwareProfileName)

            response = {'nodes': nodeList.getCleanDict()}
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API getUsableNodes() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getNodes(self, softwareProfileName):
        try:
            nodeList = self._softwareProfileManager.getNodeList(
                softwareProfileName)

            response = {
                'nodes': nodeList,
            }
        except Exception as ex:
            self.getLogger().exception(
                'software profile WS API getNodes() failed')

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
