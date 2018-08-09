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

from typing import Optional

from sqlalchemy.orm.session import Session
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.objects.parameter import Parameter
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager


class ParameterManager(TortugaObjectManager):
    def __init__(self):
        super(ParameterManager, self).__init__()

        self._globalParameterDbApi = GlobalParameterDbApi()

    def getParameter(self, session: Session, name: str) -> Parameter:
        """
        Raises:
            ParameterNotFound
        """

        return self._globalParameterDbApi.getParameter(session, name)

    def getBoolParameter(self, session: Session, name: str,
                         default: Optional[bool] = None) -> bool:
        """
        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            param = self.getParameter(session, name)
        except ParameterNotFound:
            if default is not None:
                return default

            raise

        return param.getValue() and \
            param.getValue()[0].lower() in ('1', 'y', 't')

    def getIntParameter(self, session: Session, name: str,
                        default: Optional[int] = None) -> int:
        """
        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            param = self.getParameter(name)
        except ParameterNotFound:
            if default is not None:
                return default

            raise

        return int(param.getValue())

    def getParameterList(self, session: Session) -> TortugaObjectList:
        return self._globalParameterDbApi.getParameterList(session)

    def upsertParameter(self, session: Session, parameter: Parameter) -> None:
        self._globalParameterDbApi.upsertParameter(session, parameter)

    def deleteParameter(self, session: Session, name: str) -> None:
        self._globalParameterDbApi.deleteParameter(session, name)
