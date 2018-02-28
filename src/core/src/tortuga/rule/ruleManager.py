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

import threading
from tortuga.objects.tortugaObjectManager import TortugaObjectManager


class RuleManager(TortugaObjectManager):
    # Singleton instance.
    __instanceLock = threading.RLock()

    def __init__(self, ruleObjectFactory):
        """ Initialize rule manager instance. """
        super(RuleManager, self).__init__()

        self._engine = ruleObjectFactory.getEngine()

    def getRule(self, applicationName, ruleName):
        RuleManager.__instanceLock.acquire()

        try:
            rule = self._engine.getRule(applicationName, ruleName)
            rule.encode()
            return rule
        finally:
            RuleManager.__instanceLock.release()

    def getRuleList(self):
        """ Get all known rules. """

        RuleManager.__instanceLock.acquire()

        try:
            ruleList = self._engine.getRuleList()
            ruleList.encode()
            return ruleList
        finally:
            RuleManager.__instanceLock.release()

    def addRule(self, rule):
        """ Add rule. Rule will be encoded when this method is called. """
        RuleManager.__instanceLock.acquire()
        try:
            ruleId = self._engine.addRule(rule)
            return ruleId
        finally:
            RuleManager.__instanceLock.release()

    def deleteRule(self, applicationName, ruleName):
        """ Delete rule by name. """
        RuleManager.__instanceLock.acquire()
        try:
            self._engine.deleteRule(applicationName, ruleName)
        finally:
            RuleManager.__instanceLock.release()

    def enableRule(self, applicationName, ruleName):
        """ Enable rule. """
        RuleManager.__instanceLock.acquire()
        try:
            self._engine.enableRule(applicationName, ruleName)
        finally:
            RuleManager.__instanceLock.release()

    def disableRule(self, applicationName, ruleName):
        """ Disable rule. """
        RuleManager.__instanceLock.acquire()
        try:
            self._engine.disableRule(applicationName, ruleName)
        finally:
            RuleManager.__instanceLock.release()

    def executeRule(self, applicationName, ruleName, applicationData):
        """ Execute rule. """
        RuleManager.__instanceLock.acquire()
        try:
            self._engine.\
                executeRule(applicationName, ruleName, applicationData)
        finally:
            RuleManager.__instanceLock.release()

    def receiveApplicationData(self, applicationName, applicationData):
        """ Receive applicaton data and pass it to the rule engine. """
        RuleManager.__instanceLock.acquire()
        try:
            self._engine.\
                receiveApplicationData(applicationName, applicationData)
        finally:
            RuleManager.__instanceLock.release()
