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

from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.objects.tortugaObjectManager import TortugaObjectManager


class ParameterManager(TortugaObjectManager):
    def __init__(self):
        super(ParameterManager, self).__init__()

        self._globalParameterDbApi = GlobalParameterDbApi()

    def getParameter(self, name):
        """
        Raises:
            ParameterNotFound
        """

        return self._globalParameterDbApi.getParameter(name)

    def getBoolParameter(self, name, default=None):
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

        return param.getValue() and \
            param.getValue()[0].lower() in ('1', 'y', 't')

    def getIntParameter(self, name, default=None):
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

    def getParameterList(self):
        return self._globalParameterDbApi.getParameterList()

    def upsertParameter(self, parameter):
        return self._globalParameterDbApi.upsertParameter(parameter)

    def deleteParameter(self, name):
        return self._globalParameterDbApi.deleteParameter(name)
