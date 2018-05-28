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
