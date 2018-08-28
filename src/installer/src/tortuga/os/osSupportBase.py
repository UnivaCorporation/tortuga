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
from typing import Optional

from sqlalchemy.orm.session import Session

from tortuga.config.configManager import ConfigManager
from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.objects.osFamilyInfo import OsFamilyInfo


class OsSupportBase:
    def __init__(self, osFamilyInfo: OsFamilyInfo) -> None:
        self._osFamilyInfo = osFamilyInfo
        self._logger = logging.getLogger('tortuga.os')
        self._cm = ConfigManager()

    def getLogger(self):
        return self._logger

    def getKickstartFileContents(
            self, session: Session, node: Node,
            hardwareprofile: HardwareProfile,
            softwareprofile: SoftwareProfile) -> str: \
        # pylint: disable=no-self-use,unused-argument
        """
        Returns entire Kickstart file contents
        """

        return ''

    def getPXEReinstallSnippet(
            self, ksurl: str, node: Node,
            hardwareprofile: Optional[HardwareProfile] = None,
            softwareprofile: Optional[SoftwareProfile] = None): \
            # pylint: disable=no-self-use,unused-argument
        return ''

    def deleteNodeCleanup(self, node: Node): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Called when the specified node is being deleted.  This method
        is intended to be used for cleaning up files that aren't
        natively managed by Tortuga.
        '''

    def write_other_boot_files(self, node: Node,
                               hardwareprofile: HardwareProfile,
                               softwareprofile: SoftwareProfile): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Can optionally be used to write files after node is added prior to
        node being started/booted.
        '''

    def get_cloud_config(self, node: Node, hardwareprofile: HardwareProfile,
                         softwareprofile: SoftwareProfile): \
            # pylint: disable=no-self-use,unused-argument
        '''
        Return dict containing node-specific cloud-init compatible user data
        '''

        return {}
