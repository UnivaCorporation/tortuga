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

import re
from tortuga.exceptions.invalidMacAddress import InvalidMacAddress


def fixNetworkDeviceName(networkDevice):
    lastAlpha = 0
    for i in range(0, len(networkDevice)):
        if networkDevice[i:i + 1].isalpha():
            lastAlpha = i

    return "%s0" % networkDevice[:lastAlpha + 1]


def validateMacAddress(macAddr: str) -> str:
    """
    Use a regex to validate a MAC address.  Expected format is
    xx:xx:xx:xx:xx:xx

    Raises:
        InvalidMacAddress
    """

    if not macAddr:
        raise InvalidMacAddress('MAC address is empty/undefined')

    if not re.compile(
            r'^([0-9A-Fa-f]{2}[:-]?){5}[0-9A-Fa-f]{2}([:-]?.*){0,1}$').\
            match(macAddr):
        raise InvalidMacAddress(
            'MAC address [%s] is invalid/malformed' % (macAddr))

    # If the MAC address was provided unformatted, insert the separators
    if '-' in macAddr:
        tmpMacAddr = macAddr.replace('-', ':')
        return tmpMacAddr.lower()

    if ':' not in macAddr:
        tmpMacAddr = '%s:%s:%s:%s:%s:%s' % (macAddr[0:2],
                                            macAddr[2:4],
                                            macAddr[4:6],
                                            macAddr[6:8],
                                            macAddr[8:10],
                                            macAddr[10:12])

        return tmpMacAddr.lower()

    # Fall through
    return macAddr
