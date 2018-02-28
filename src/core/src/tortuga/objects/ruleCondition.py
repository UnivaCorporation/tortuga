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


class RuleCondition(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'condition'

    def __init__(self, metricXPath='', evaluationOperator='',
                 triggerValue=''):
        TortugaObject.__init__(
            self, {
                'metricXPath': metricXPath,
                'evaluationOperator': evaluationOperator,
                'triggerValue': triggerValue,
            }, ['metricXPath', 'evaluationOperator', 'triggerValue', 'id'],
            RuleCondition.ROOT_TAG, {
                'evaluationOperator': 'str',
            })

    def setId(self, id_):
        self['id'] = id_

    def getId(self):
        return self.get('id')

    def setMetricXPath(self, metricXPath):
        self['metricXPath'] = metricXPath

    def getMetricXPath(self):
        return self.get('metricXPath')

    def setEvaluationOperator(self, evaluationOperator):
        self['evaluationOperator'] = evaluationOperator

    def getEvaluationOperator(self):
        return self.get('evaluationOperator')

    def setTriggerValue(self, triggerValue):
        self['triggerValue'] = triggerValue

    def getTriggerValue(self):
        return self.get('triggerValue')

    def setDescription(self, description):
        self['description'] = description

    def getDescription(self):
        return self.get('description')

    @staticmethod
    def getKeys():
        return [
            'id', 'metricXPath', 'evaluationOperator', 'triggerValue',
            'description'
        ]
