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

import tortuga.objects.parameter
from tortuga.parameter.parameterApiInterface import ParameterApiInterface
from tortuga.exceptions.tortugaException import TortugaException
from .tortugaWsApi import TortugaWsApi


class ParameterWsApi(TortugaWsApi, ParameterApiInterface):
    """
    Parameter WS API class.
    """

    def getParameter(self, name):
        """
        Get parameter.

            Returns:
                parameter
            Throws:
                ParameterNotFound
                TortugaException
        """

        url = 'v1/parameters/%s' % (name)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.parameter.Parameter.getFromDict(
                responseDict.get('globalparameter'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getParameterList(self):
        """
        Get all known parameters.

            Returns:
                [parameter]
            Throws:
                TortugaException
        """

        url = 'v1/parameters'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return tortuga.objects.parameter.Parameter.getListFromDict(
                responseDict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
