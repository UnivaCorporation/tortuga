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


class BootHostManagerInterface(object):
    def rmPXEFile(self, nodename): \
            # pylint: disable=no-self-use,unused-argument
        """
        Clean up existing PXE configuration
        """
        raise AbstractMethod(
            'rmPXEFile() must be overriden in the derived class.')

    def writePXEFile(self, node, localboot=None, hardwareProfile=None,
                     softwareProfile=None): \
            # pylint: disable=no-self-use,unused-argument
        raise AbstractMethod(
            'writePXEFile() must be overriden in the derived class.')

    def getTftproot(self): \
            # pylint: disable=no-self-use
        raise AbstractMethod(
            'getTftproot() must be overridden in the derived class.')

    def get_cloud_config(self, node, hardwareprofile, softwareprofile): \
            # pylint: disable=no-self-use,unused-argument
        """
        Get cloud-init compatible cloud config for node
        """

        raise AbstractMethod(
            'get_cloud_config() must be overridden in the derived class.')

    def write_other_boot_files(self, node, hardwareprofile, softwareprofile): \
            # pylint: disable=no-self-use,unused-argument
        """
        Write node-specific files required for booting
        """

    def deleteNodeCleanup(self, node): \
            # pylint: disable=no-self-use,unused-argument
        """
        Perform OS specific node boot file cleanup
        """
