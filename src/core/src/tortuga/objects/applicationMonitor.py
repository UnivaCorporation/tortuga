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
import time


class ApplicationMonitor(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'applicationMonitor'

    def __init__(self, type_='', description='', pollPeriod=None):
        TortugaObject.__init__(
            self, {
                'type': type_,
                'description': description,
                'pollPeriod': pollPeriod,
            },
            ['type', 'id', 'pollPeriod', 'maxActionInvocations'],
            ApplicationMonitor.ROOT_TAG, {
                'queryCommand': 'str',
                'actionCommand': 'str',
            }
        )

    def setId(self, id_):
        self['id'] = id_

    def getId(self):
        return self.get('id')

    def setType(self, type_):
        self['type'] = type_

    def getType(self):
        return self.get('type')

    def setDescription(self, description):
        self['description'] = description

    def getDescription(self):
        return self.get('description')

    def setPollPeriod(self, pollPeriod):
        self['pollPeriod'] = pollPeriod

    def getPollPeriod(self):
        return self.get('pollPeriod')

    def setQueryCommand(self, queryCommand):
        self['queryCommand'] = queryCommand

    def getQueryCommand(self):
        return self.get('queryCommand')

    def setAnalyzeCommand(self, analyzeCommand):
        self['analyzeCommand'] = analyzeCommand

    def getAnalyzeCommand(self):
        return self.get('analyzeCommand')

    def setActionCommand(self, actionCommand):
        self['actionCommand'] = actionCommand

    def getActionCommand(self):
        return self.get('actionCommand')

    def setMaxActionInvocations(self, maxActionInvocations):
        self['maxActionInvocations'] = maxActionInvocations

    def getMaxActionInvocations(self):
        return self.get('maxActionInvocations')

    def getTotalQueryInvocations(self):
        return self.get('totalQueryInvocations')

    def getSuccessfulQueryInvocations(self):
        return self.get('successfulQueryInvocations')

    def getFailedQueryInvocations(self):
        return self.get('failedQueryInvocations')

    def getLastSuccessfulQueryInvocationTime(self):
        return self.get('lastSuccessfulQueryInvocationTime')

    def getLastFailedQueryInvocationTime(self):
        return self.get('lastFailedQueryInvocationTime')

    def queryInvocationSucceeded(self):
        if not self.get('successfulQueryInvocations'):
            if not self.get('failedQueryInvocations'):
                self['failedQueryInvocations'] = 0
            if not self.get('totalQueryInvocations'):
                self['totalQueryInvocations'] = 0
            self['successfulQueryInvocations'] = 0
        self['successfulQueryInvocations'] += 1
        self['totalQueryInvocations'] += 1
        self['lastSuccessfulQueryInvocationTime'] = time.time()

    def queryInvocationFailed(self):
        if not self.get('failedQueryInvocations'):
            if not self.get('successfulQueryInvocations'):
                self['successfulQueryInvocations'] = 0
            if not self.get('totalQueryInvocations'):
                self['totalQueryInvocations'] = 0
            self['failedQueryInvocations'] = 0
        self['failedQueryInvocations'] += 1
        self['totalQueryInvocations'] += 1
        self['lastFailedQueryInvocationTime'] = time.time()

    def getTotalActionInvocations(self):
        return self.get('totalActionInvocations')

    def getSuccessfulActionInvocations(self):
        return self.get('successfulActionInvocations')

    def getFailedActionInvocations(self):
        return self.get('failedActionInvocations')

    def getLastSuccessfulActionInvocationTime(self):
        return self.get('lastSuccessfulActionInvocationTime')

    def getLastFailedActionInvocationTime(self):
        return self.get('lastFailedActionInvocationTime')

    def actionInvocationSucceeded(self):
        if not self.get('successfulActionInvocations'):
            if not self.get('failedActionInvocations'):
                self['failedActionInvocations'] = 0
            if not self.get('totalActionInvocations'):
                self['totalActionInvocations'] = 0
            self['successfulActionInvocations'] = 0
        self['successfulActionInvocations'] += 1
        self['totalActionInvocations'] += 1
        self['lastSuccessfulActionInvocationTime'] = time.time()

    def actionInvocationFailed(self):
        if not self.get('failedActionInvocations'):
            if not self.get('successfulActionInvocations'):
                self['successfulActionInvocations'] = 0
            if not self.get('totalActionInvocations'):
                self['totalActionInvocations'] = 0
            self['failedActionInvocations'] = 0
        self['failedActionInvocations'] += 1
        self['totalActionInvocations'] += 1
        self['lastFailedActionInvocationTime'] = time.time()

    @staticmethod
    def getKeys():
        return [
            'id',
            'type',
            'description',
            'pollPeriod',
            'queryCommand',
            'analyzeCommand',
            'actionCommand',
            'maxActionInvocations',
            'failedQueryInvocations',
            'successfulQueryInvocations',
            'totalQueryInvocations',
            'lastFailedQueryInvocationTime',
            'lastSuccessfulQueryInvocationTime',
            'failedActionInvocations',
            'successfulActionInvocations',
            'totalActionInvocations',
            'lastFailedActionInvocationTime',
            'lastSuccessfulActionInvocationTime',
        ]
