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
from tortuga.exceptions.ruleNotFound import RuleNotFound
from tortuga.web_service.ruleManager import ruleManager, ruleObjectFactory
from .tortugaController import TortugaController
from .authController import AuthController, require


class RuleController(TortugaController):
    """
    Rule admin controller class.

    """
    actions = [
        {
            'name': 'getRuleList',
            'path': '/v1/rules',
            'action': 'getRuleList',
            'method': ['GET'],
        },
        {
            'name': 'getRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)',
            'action': 'getRule',
            'method': ['GET'],
        },
        {
            'name': 'deleteRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)',
            'action': 'deleteRule',
            'method': ['DELETE'],
        },
        {
            'name': 'addRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)',
            'action': 'addRule',
            'method': ['POST'],
        },
        {
            'name': 'disableRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)'
                    '/disable',
            'action': 'disableRule',
            'method': ['PUT'],
        },
        {
            'name': 'enableRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)'
                    '/enable',
            'action': 'enableRule',
            'method': ['PUT'],
        },
        {
            'name': 'executeRule',
            'path': '/v1/rules/:(application_name)/name/:(rule_name)'
                    '/execute',
            'action': 'executeRule',
            'method': ['PUT'],
        },
    ]

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getRule(self, application_name, rule_name):
        """ Return info for the specified rule. """

        try:
            rule = ruleManager.getRule(application_name, rule_name)

            response = {
                'rule': rule.getCleanDict(),
            }
        except Exception as ex:
            self.getLogger().error(
                '[{0}] getRule() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getRuleList(self):
        """ Return list of all available rules. """

        try:
            ruleList = ruleManager.getRuleList()

            response = {
                'rules': ruleList.getCleanDict(),
            }
        except Exception as ex:
            self.getLogger().error(
                '[{0}] getRuleList() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addRule(self, application_name, rule_name):
        """ Add rule. """

        postdata = cherrypy.request.json

        # Check arguments.
        if 'rule' not in postdata:
            raise cherrypy.HTTPError(400, 'Missing rule data.')

        if 'xml' not in postdata['rule']:
            raise InvalidArgument('Missing XML rule data')

        parser = ruleObjectFactory.getParser()

        rule = parser.parseString(postdata['rule']['xml'])

        if rule.getApplicationName() != application_name:
            raise InvalidArgument(
                'Inconsistent application name %s for rule %s' % (
                    application_name, rule))

        if rule.getName() != rule_name:
            raise InvalidArgument(
                'Inconsistent rule name %s for rule %s' % (
                    rule_name, rule))

        try:
            rule_id = ruleManager.addRule(rule)

            response = {
                'rule': {
                    'id': rule_id,
                }
            }
        except Exception as ex:
            self.getLogger().exception(
                '[{0}] addRule() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deleteRule(self, application_name, rule_name):
        """Remove rule"""

        response = None

        try:
            ruleManager.deleteRule(application_name, rule_name)
        except Exception as ex:
            if not isinstance(ex, RuleNotFound):
                self.getLogger().exception(
                    '[{0}] deleteRule() raised an exception'.format(
                        self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def enableRule(self, application_name, rule_name):
        """Enable rule"""

        response = None

        try:
            ruleManager.enableRule(application_name, rule_name)
        except Exception as ex:
            self.getLogger().exception(
                '[{0}] enableRule() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def disableRule(self, application_name, rule_name):
        """ Disable rule. """

        response = None

        try:
            ruleManager.disableRule(application_name, rule_name)
        except Exception as ex:
            self.getLogger().exception(
                '[{0}] disableRule() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)

    @require()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def executeRule(self, application_name, rule_name):
        """ Execute rule. """

        response = None

        postdata = cherrypy.request.json

        applicationData = postdata['data'] if 'data' in postdata else None

        try:
            ruleManager.executeRule(
                application_name, rule_name, applicationData)
        except Exception as ex:
            self.getLogger().exeption(
                '[{0}] executeRule() raised an exception'.format(
                    self.__class__.__name__))

            self.handleException(ex)

            response = self.errorResponse(str(ex))

        return self.formatResponse(response)
