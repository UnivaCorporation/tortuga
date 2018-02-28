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

from tortuga.exceptions.abstractMethod import AbstractMethod


class RuleEngineInterface(object):
    """
    Rule engine interface.
    """

    def hasRule(self, ruleId): \
            # pylint: disable=no-self-use,unused-argument
        """
        Does engine know about the given rule.

            Returns:
                True if rule is known, False otherwise.
            Throws:
                None
        """
        raise AbstractMethod('hasRule() has to be implemented in the'
                             ' concrete API class.')

    def addRule(self, rule): \
            # pylint: disable=no-self-use,unused-argument
        """
        Add rule.

            Returns:
                ruleId
            Throws:
                UserNotAuthorized
                RuleAlreadyExists
                InvalidXml
                TortugaException
        """
        raise AbstractMethod('addRule() has to be implemented in the'
                             ' concrete API class.')

    def deleteRule(self, applicationName, ruleName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Delete rule.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                TortugaException
        """
        raise AbstractMethod('deleteRule() has to be implemented in the'
                             ' concrete API class.')

    def getRule(self, applicationName, ruleName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get rule info.

            Returns:
                rule
            Throws:
                UserNotAuthorized
                RuleNotFound
                TortugaException
        """
        raise AbstractMethod('getRule() has to be implemented in the'
                             ' concrete API class.')

    def getRuleList(self): \
            # pylint: disable=no-self-use
        """
        Get all known rules.

            Returns:
                [rule]
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod('getRuleList() has to be implemented in the'
                             ' concrete API class.')

    def receiveApplicationData(self, applicationName, applicationData): \
            # pylint: disable=no-self-use,unused-argument
        """
        Receive (and process) application monitoring data.

            Returns:
                None
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod('receiveApplicationData() has to be'
                             ' implemented in the concrete API class.')
