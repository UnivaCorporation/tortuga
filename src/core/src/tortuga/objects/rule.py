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

from tortuga.objects.tortugaObject import TortugaObject
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects import applicationMonitor
from tortuga.objects import ruleCondition
from tortuga.objects import xPathVariable

import time


class Rule(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'rule'
    ENABLED_STATUS = 'enabled'
    DISABLED_STATUS = 'disabled'

    def __init__(self, applicationName='', name='', description=''):
        TortugaObject.__init__(self, {
            'applicationName': applicationName,
            'name': name,
            'description': description,
            'status': Rule.ENABLED_STATUS,
            'conditions': TortugaObjectList(),
            'xPathVariables': TortugaObjectList(),
        }, ['applicationName', 'name', 'id'], Rule.ROOT_TAG)

    def setId(self, id_):
        self['id'] = id_

    def getId(self):
        id_ = self.get('id')

        if not id_:
            return getRuleId(self.getApplicationName(), self.getName())

        return id_

    def setName(self, name):
        self['name'] = name

    def getName(self):
        return self.get('name')

    def setApplicationName(self, applicationName):
        self['applicationName'] = applicationName

    def getApplicationName(self):
        return self.get('applicationName')

    def setDescription(self, description):
        self['description'] = description

    def getDescription(self):
        return self.get('description')

    def addCondition(self, condition):
        self['conditions'].append(condition)

    def setConditionList(self, conditions):
        self['conditions'] = conditions

    def getConditionList(self):
        return self['conditions']

    def setApplicationMonitor(self, applicationMonitor_):
        self['applicationMonitor'] = applicationMonitor_

    def getApplicationMonitor(self):
        return self.get('applicationMonitor')

    def getTotalInvocations(self):
        return self.get('totalInvocations')

    def getLastInvocationTime(self):
        return self.get('lastInvocationTime')

    def ruleInvoked(self):
        if not self.get('totalInvocations'):
            self['totalInvocations'] = 1
        else:
            self['totalInvocations'] += 1
        self['lastInvocationTime'] = time.time()

    def getType(self):
        appMonitor = self.getApplicationMonitor()
        return appMonitor.getType() if appMonitor else 'unknown'

    def __repr__(self):
        return '%s (type: %s, status: %s)' % (
            getRuleId(self.getApplicationName(), self.getName()),
            self.getType(), self.getStatus())

    def addXPathVariable(self, xPathVariable_):
        self['xPathVariables'].append(xPathVariable_)

    def setXPathVariableList(self, xPathVariables):
        self['xPathVariables'] = xPathVariables

    def getXPathVariableList(self):
        return self['xPathVariables']

    def setStatus(self, status):
        self['status'] = status

    def getStatus(self):
        return self['status']

    def setStatusEnabled(self):
        self['status'] = Rule.ENABLED_STATUS

    def isStatusEnabled(self):
        return self['status'] == Rule.ENABLED_STATUS

    @staticmethod
    def getKeys():
        return [
            'id', 'name', 'applicationName', 'description',
            'totalInvocations', 'lastInvocationTime', 'status'
        ]

    @classmethod
    def getFromDict(cls, _dict):
        """ Get rule from _dict. """

        # Populate the static fields
        rule = super(Rule, cls).getFromDict(_dict)

        appMonitorDict = _dict.get(
            applicationMonitor.ApplicationMonitor.ROOT_TAG)

        if appMonitorDict:
            rule.setApplicationMonitor(
                applicationMonitor.ApplicationMonitor.getFromDict(
                    appMonitorDict))

        rule.setConditionList(ruleCondition.RuleCondition.getListFromDict(
            _dict))

        rule.setXPathVariableList(
            xPathVariable.XPathVariable.getListFromDict(_dict))

        return rule


def getRuleId(applicationName, ruleName):
    """ Form rule id. """
    return '%s/%s' % (applicationName, ruleName)
