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

from tortuga.exceptions.abstractMethod import AbstractMethod


class ParameterApiInterface(object):
    """
    Parameter API interface.
    """

    def getParameter(self, name): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get parameter.

            Returns:
                parameter
            Throws:
                ParameterNotFound
                TortugaException
        """
        raise AbstractMethod(
            'getParameter() has to be implemented in the concrete API'
            ' class.')

    def getBoolParameter(self, name, default=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get bool parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        raise AbstractMethod(
            'getBoolParameter() has to be implemented in the concrete API'
            ' class.')

    def getIntParameter(self, name, default=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get bool parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        raise AbstractMethod(
            'getIntParameter() has to be implemented in the concrete API'
            ' class.')

    def getParameterList(self): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get all known parameters.

            Returns:
                [parameter]
            Throws:
                TortugaException
        """
        raise AbstractMethod(
            'getParameterList() has to be implemented in the concrete API'
            ' class.')
