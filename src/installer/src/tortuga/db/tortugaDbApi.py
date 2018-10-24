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

import logging
from typing import Dict

from tortuga.exceptions.invalidDbRelation import InvalidDbRelation
from tortuga.objects.tortugaObject import TortugaObjectList


class TortugaDbApi:
    """
    Base DB API class.
    """

    def __init__(self):
        self._logger = logging.getLogger(
            'tortuga.db.%s' % (self.__class__.__name__))

    def getLogger(self):
        """ Logger for this class. """
        return self._logger

    def loadRelation(self, dbObject, relationName): \
            # pylint: disable=no-self-use
        if relationName not in dir(dbObject):
            raise InvalidDbRelation(
                'Relation %s not valid for class %s' % (
                    relationName, dbObject.__class__.__name__))

        o = None

        # pylint: disable=exec-used
        exec('o = dbObject.%s' % (relationName))

        return o

    def loadRelations(self, dbObject,
                      optionDict: Dict[str, bool] = None) -> None:
        if optionDict:
            for k in list(optionDict.keys()):
                # The optionDict contains key-value pairs of relation name
                # and a boolean to indicate whether to load that relation
                if not optionDict[k]:
                    continue

                try:
                    self.loadRelation(dbObject, k)
                except InvalidDbRelation:
                    self.getLogger().exception(
                        'Relation [{}] not valid'.format(k))

                    raise

    def getTortugaObjectList(self, cls, dbList): \
            # pylint: disable=no-self-use
        return TortugaObjectList([
            cls.getFromDbDict(dbItem.__dict__) for dbItem in dbList])
