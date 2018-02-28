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

from tortuga.exceptions.invalidProfileName import InvalidProfileName


def validateProfileName(profileName):
    """
    Simple validation for hardware & software profile names.  Extend
    as necessary...
    """

    if not profileName:
        raise InvalidProfileName('Profile name not specified')

    try:
        if re.compile(r'\A[A-Za-z0-9]+').match(profileName):
            return
    except UnicodeDecodeError:
        pass

    raise InvalidProfileName(
        'Profile name [%s] is invalid/malformed' % (
            profileName.encode('ascii', 'replace')))
