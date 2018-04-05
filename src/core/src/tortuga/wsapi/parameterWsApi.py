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
from tortuga.exceptions.tortugaException import TortugaException
from .tortugaWsApi import TortugaWsApi


class ParameterWsApi(TortugaWsApi):
    """
    Parameter WS API class.

    """
    def getParameter(self, name):
        """
        Gets a parameter.

        :param name: the name of the parameter to get
        :return: a parameter
        :raises ParameterNotFound:

        """
        url = 'v1/parameters/%s' % (name)

        try:
            _, response_dict = self.sendSessionRequest(url)

            return tortuga.objects.parameter.Parameter.getFromDict(
                response_dict.get('globalparameter'))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getParameterList(self):
        """
        Get all known parameters.

        :return: a list of parameters

        """
        url = 'v1/parameters'

        try:
            _, response_dict = self.sendSessionRequest(url)

            return tortuga.objects.parameter.Parameter.getListFromDict(
                response_dict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def createParameter(self, parameter):
        """
        Create a parameter.

        :param parameter: the parameter to create

        """
        url = 'v1/parameters'
        data = parameter.getJsonRep()

        try:
            _, response_dict = self.sendSessionRequest(url, data=data,
                                                       method='POST')
            return response_dict
        
        except TortugaException:
            raise
        
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateParameter(self, parameter):
        """
        Update a parameter.

        :param parameter: the parameter to update

        """
        url = 'v1/parameters/{}'.format(parameter.getName())

        try:
            _, response_dict = self.sendSessionRequest(url, method='PUT')
            return response_dict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteParameter(self, name):
        """
        Delete a parameter.

        :param name: the name of the parameter to delete

        """
        url = 'v1/parameters/{}'.format(name)

        try:
            _, response_dict = self.sendSessionRequest(url, method='DELETE')
            return response_dict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)
