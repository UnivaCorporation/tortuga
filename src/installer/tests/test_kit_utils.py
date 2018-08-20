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

import os

import pytest
from tortuga.kit.builder import KitBuilder
from tortuga.kit.utils import get_metadata_from_archive


@pytest.fixture()
def test_kit_archive(request) -> str:
    """
    Gets the path to the test kit archive.

    :param request: the current pytest request

    :return str: the path to the test kit archive

    """
    working_directory = os.path.join(request.fspath.dirname, 'fixtures',
                                     'kit-test')
    builder = KitBuilder(working_directory=working_directory)

    builder.clean()
    tarball_path = builder.build()

    return tarball_path


def test_get_metadata_from_archive(test_kit_archive):
    #
    # Make sure there are no exceptions in this process
    #
    get_metadata_from_archive(test_kit_archive)
