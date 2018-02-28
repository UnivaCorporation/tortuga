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

import re
import subprocess

from tortuga.os_objects.osAddHostManagerInterface \
    import OsAddHostManagerInterface
from tortuga.os_objects.osObjectManager import OsObjectManager


class AddHostManager(OsObjectManager, OsAddHostManagerInterface):
    def __init__(self):
        OsObjectManager.__init__(self)

        self._dhcpReqRegex = re.compile(
            r': BOOTP\/DHCP, Request from (.[^\s]*) ')

    def dhcpCaptureSubprocess(self, captureDeviceName):
        snoopCmd = (
            'tcpdump -l -i %s port bootpc and src 0.0.0.0 and ip broadcast')

        p1 = subprocess.Popen(snoopCmd % (captureDeviceName),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True)

        return p1

    def getMacAddressFromCaptureEntry(self, capturedLine):
        """
        Parse the entry from the packet capture

        Returns a valid MAC address, otherwise returns None
        """

        m = self._dhcpReqRegex.search(capturedLine)

        if not m:
            return None

        mac = m.group(1)

        return mac
