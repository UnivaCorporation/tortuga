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

from tortuga.config import version_is_compatible, VERSION


def test_version_is_compatible():
    #
    # Make sure the exact same version is compatible
    #
    assert version_is_compatible(VERSION)

    #
    # Make sure future version is not compatible
    #
    assert not version_is_compatible('10.0.0')

    #
    # Make sure past verion is compatible
    #
    assert version_is_compatible('0.0.1')
