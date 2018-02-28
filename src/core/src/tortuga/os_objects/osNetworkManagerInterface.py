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


class OsNetworkManagerInterface(object):
    """
    OS file system manager interface.
    """

    def findNics(self, device=None): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return a list of nics and dict containing properties for those nics
        """
        raise AbstractMethod(
            'findNics() has to be implemented in the concrete API class.')

    def getNetworkInterfaces(self): \
            # pylint: disable=no-self-use
        """
        Return list of network interfaces on installer as reported by
        "facter interfaces"
        """

        raise AbstractMethod(
            'getNetworkInterfaces has to be implemented in the concrete'
            ' API class.')
