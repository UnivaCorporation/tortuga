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

from tortuga.parameter.parameterManager import ParameterManager
from tortuga.parameter.parameterApiInterface import ParameterApiInterface
from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException


class ParameterApi(TortugaApi, ParameterApiInterface):
    """
    Parameter API class.
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

        try:
            return ParameterManager().getParameter(name)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getBoolParameter(self, name, default=None):
        """
        Get bool parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            return ParameterManager().getBoolParameter(
                name, default)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getIntParameter(self, name, default=None):
        """
        Get int parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            return ParameterManager().getIntParameter(
                name, default)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getParameterList(self):
        """
        Get all known parameters.

            Returns:
                [parameter]
            Throws:
                TortugaException
        """

        try:
            return ParameterManager().getParameterList()
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise TortugaException(exception=ex)

    def upsertParameter(self, parameter):
        try:
            return ParameterManager().upsertParameter(parameter)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error upserting parameter [%s]' % (parameter.getName()))

            raise TortugaException(exception=ex)

    def deleteParameter(self, name):
        """
        Delete parameter by name
        """

        try:
            return ParameterManager().deleteParameter(name)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error deleting parameter [%s]' % (name))

            raise TortugaException(exception=ex)
