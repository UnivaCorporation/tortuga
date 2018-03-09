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

# pylint: disable=no-member,maybe-no-member

import json
import base64
import urllib.request, urllib.parse, urllib.error

from tortuga.objects import rule
from tortuga.exceptions.tortugaException import TortugaException
from .tortugaWsApi import TortugaWsApi


class RuleWsApi(TortugaWsApi):
    """
    Rule WS API class.
    """

    def getRule(self, applicationName, ruleName):
        """
        Get rule info.

            Returns:
                rule
            Throws:
                RuleNotFound
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}'.format(
            urllib.parse.quote_plus(applicationName),
            urllib.parse.quote_plus(ruleName))

        try:
            _, responseDict = self.sendSessionRequest(url)

            r = rule.Rule.getFromDict(responseDict.get('rule'))

            r.decode()

            return r
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getRuleList(self):
        """
        Get rule list.

            Returns:
                [rules]
            Throws:
                TortugaException
        """

        url = 'v1/rules'

        try:
            _, responseDict = self.sendSessionRequest(url)

            ruleList = rule.Rule.getListFromDict(responseDict)

            ruleList.decode()

            return ruleList
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addRule(self, r):
        """
        Add rule.

            Returns:
                (none)
            Throws:
                UserNotAuthorized
                RuleAlreadyExists
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}'.format(
            urllib.parse.quote_plus(r.getApplicationName()),
            urllib.parse.quote_plus(r.getName()))

        try:
            r.encode()

            postdata = {
                'rule': {
                    'xml': r.getXmlRep(),
                }
            }

            self.sendSessionRequest(
                url, method='POST', data=json.dumps(postdata))

            r.decode()
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteRule(self, applicationName, ruleName):
        """
        Delete rule.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}'.format(
            urllib.parse.quote_plus(applicationName),
            urllib.parse.quote_plus(ruleName))

        try:
            self.sendSessionRequest(url, method='DELETE')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def postApplicationData(self, applicationName, applicationData):
        """
        Send application monitoring data.

            Returns:
                None
            Throws:
                TortugaException
        """

        url = 'v1/applications/{0}/data'.format(
            urllib.parse.quote_plus(applicationName))

        postdata = {
            'data': base64.b64encode(base64.encodestring(applicationData)),
        }

        try:
            self.sendSessionRequest(
                url, method='POST', data=json.dumps(postdata))
        except TortugaException as ex:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def enableRule(self, applicationName, ruleName):
        """
        Enable rule that has been disabled.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleAlreadyEnabled
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}/enable'.format(
            urllib.parse.quote_plus(applicationName),
            urllib.parse.quote_plus(ruleName))

        postdata = {}

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(postdata))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def disableRule(self, applicationName, ruleName):
        """
        Disable rule that is currently enabled.

            Returns:
                (none)
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleAlreadyDisabled
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}/disable'.format(
            urllib.parse.quote_plus(applicationName),
            urllib.parse.quote_plus(ruleName))

        postdata = {}

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(postdata))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def executeRule(self, applicationName, ruleName, applicationData=''):
        """
        Execute rule.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleDisabled
                TortugaException
        """

        url = 'v1/rules/{0}/name/{1}/execute'.format(
            urllib.parse.quote_plus(applicationName),
            urllib.parse.quote_plus(ruleName))

        postdata = applicationData if applicationData else {}

        try:
            self.sendSessionRequest(
                url, method='PUT', data=json.dumps(dict(data=postdata)))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
