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

import logging
from tortuga.config.configManager import ConfigManager


class OsSupportBase(object):
    def __init__(self, osFamilyInfo):
        self._osFamilyInfo = osFamilyInfo
        self._logger = logging.getLogger('tortuga.os')
        self._logger.addHandler(logging.NullHandler())
        self._cm = ConfigManager()

    def getLogger(self):
        return self._logger

    def getKickstartFileContents(self, node, hardwareprofile,
                                 softwareprofile): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Returns a string representing the boot file.  For example, the
        Kickstart file on RHEL-based derivatives.

        Note: 'dbNode' is an instance of Nodes (the SQLAlchemy
        representation of the Nodes table), it is *not* a Node
        TortugaObject
        '''

        return ''

    def getPXEReinstallSnippet(self, ksurl, node, hardwareprofile=None,
                               softwareprofile=None): \
            # pylint: disable=no-self-use,unused-argument
        return ''

    def deleteNodeCleanup(self, node): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Called when the specified node is being deleted.  This method
        is intended to be used for cleaning up files that aren't
        natively managed by Tortuga.
        '''

    def write_other_boot_files(self, node, hardwareprofile, softwareprofile): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Can optionally be used to write files after node is added prior to
        node being started/booted.
        '''

    def get_cloud_config(self, node, hardwareprofile, softwareprofile): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Return dict containing node-specific cloud-init compatible user data
        '''

        return {}
