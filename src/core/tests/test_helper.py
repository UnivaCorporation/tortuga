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

import pytest

from tortuga.utility.helper import str2bool


@pytest.mark.parametrize('argument,expected', [
    ('true', True),
    ('false', False),
    ('True', True),
    ('False', False),
    (True, True),
    (False, False),
    ('t', True),
    ('y', True),
    ('1', True),
    ('f', False),
    (None, False),
    ])
def test_str2bool(argument, expected):
    result = str2bool(argument)

    assert result == expected


def test_str2bool_with_default_override():
    result = str2bool(None, default=True)

    assert result
