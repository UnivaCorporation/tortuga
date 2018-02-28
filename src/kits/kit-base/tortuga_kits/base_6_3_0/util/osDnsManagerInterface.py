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

from tortuga.exceptions.abstractMethod import AbstractMethod


class OsDnsManagerInterface(object):
    """
    OS dns manager interface.
    """

    def getServiceConfigFile(self): \
            # pylint: disable=no-self-use
        """
        Get service configuration file.

            Returns:
                Service configuration file name
            Throws:
                None
        """
        raise AbstractMethod(
            'getServiceConfigFile() has to be implemented in the derived'
            ' class.')

    def getConfigDir(self): \
            # pylint: disable=no-self-use
        """
        Get configuration directory.

            Returns:
                Configuration directory
            Throws:
                None
        """
        raise AbstractMethod(
            'getConfigDir() has to be implemented in the derived class.')

    def getServiceName(self): \
            # pylint: disable=no-self-use
        """
        Get service name.

            Returns:
                Service name
            Throws:
                None
        """
        raise AbstractMethod(
            'getServiceName() has to be implemented in the derived class.')
