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


class RuleApiInterface(object):
    """
    Rule API interface.
    """

    def getRule(self, applicationName, ruleName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get rule info.

            Returns:
                rule
            Throws:
                RuleNotFound
                TortugaException
        """
        raise AbstractMethod('getRule() has to be implemented in the'
                             ' concrete API class.')

    def getRuleList(self): \
            # pylint: disable=no-self-use
        """
        Get rule list.

            Returns:
                [rules]
            Throws:
                TortugaException
        """
        raise AbstractMethod('getRuleList() has to be implemented in the'
                             ' concrete API class.')

    def addRule(self, rule): \
            # pylint: disable=no-self-use,unused-argument
        """
        Install rule using rule name/version/iteration.

            Returns:
                ruleId
            Throws:
                UserNotAuthorized
                FileNotFound
                InvalidXml
                RuleAlreadyExists
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

    def enableRule(self, applicationName, ruleName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Enable rule using rule name/version/iteration.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleAlreadyEnabled
                TortugaException
        """
        raise AbstractMethod('enableRule() has to be implemented in the'
                             ' concrete API class.')

    def disableRule(self, applicationName, ruleName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Disable rule using rule name/version/iteration.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleAlreadyDisabled
                TortugaException
        """
        raise AbstractMethod('disableRule() has to be implemented in the'
                             ' concrete API class.')

    def executeRule(self, applicationName, ruleName, applicationData): \
            # pylint: disable=no-self-use,unused-argument
        """
        Execute rule using rule name/version/iteration.

            Returns:
                None
            Throws:
                UserNotAuthorized
                RuleNotFound
                RuleDisabled
                TortugaException
        """
        raise AbstractMethod('executeRule() has to be implemented in the'
                             ' concrete API class.')

    def postApplicationData(self, applicationName, applicationData): \
            # pylint: disable=no-self-use,unused-argument
        """
        Post application data to the rule engine.

            Returns:
                None
            Throws:
                UserNotAuthorized
                TortugaException
        """
        raise AbstractMethod('postApplicationData() has to be implemented'
                             ' in the concrete API class.')
