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
