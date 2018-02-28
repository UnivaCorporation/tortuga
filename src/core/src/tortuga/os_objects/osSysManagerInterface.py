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


class OsSysManagerInterface(object):
    """
    General system manager interface.
    """

    def findTimeInfo(self): \
            # pylint: disable=no-self-use
        """
        Return a tuple containing timezone and UTC flag (True/False)
        """
        raise AbstractMethod('findTimeInfo() must be implemented')

    def getKernel(self, osinfo): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return kernel name for specified osInfo
        """
        raise AbstractMethod('getKernel() must be implemented')

    def getInitrd(self, osinfo): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return initrd for specified osInfo
        """
        raise AbstractMethod('getInitrd() must be implemented')

    def getSudoCommand(self): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return equivalent of the sudo command for the given OS
        """
        raise AbstractMethod('getSudoCommand() must be implemented')

    def getSudoInitScript(self): \
            # pylint: disable=no-self-use,unused-argument
        """
        Return script that initializes equivalent of the sudo command for
        the given OS
        """
        raise AbstractMethod('getSudoInitScript() must be implemented')

    def getTarCommand(self): \
            # pylint: disable=no-self-use
        """
        Return the GNU tar command.
        """
        raise AbstractMethod(
            'getTarCommand() must be implemented in the base class')
