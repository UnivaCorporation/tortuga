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


class OsPackageManagerInterface(object):
    """
    OS package manager interface.
    """

    def buildPackageUrl(self, host, kitName, kitVersion, arch, isOs,
                        portNum): \
            # pylint: disable=no-self-use,unused-argument
        """
        Build up a URL based on some kit properties

            Returns:
                A url to a tortuga kit based on input
            Throws:
                None
        """
        raise AbstractMethod(
            'buildPackageUrl() has to be implemented in the concrete API'
            ' class.')

    def removePackageSource(self, packageSourceName): \
            # pylint: disable=no-self-use,unused-argument
        """
        Remove package yum repo config file

            Returns:
                None
            Throws:
                CommandFailed
        """
        raise AbstractMethod(
            'removePackageSource() has to be implemented in the concrete'
            ' API class.')

    def getPackageSourceNames(self): \
            # pylint: disable=no-self-use
        """
        Get list of package source names.

            Returns:
                [packageSourceNames]
        """
        raise AbstractMethod(
            'getPackageSourceNames() has to be implemented in the concrete'
            ' API class.')
