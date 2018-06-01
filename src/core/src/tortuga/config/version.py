from distutils.version import LooseVersion


VERSION = '6.3.1-alpha+002'


def version_is_compatible(version_string: str):
    return LooseVersion(VERSION) >= LooseVersion(version_string)
