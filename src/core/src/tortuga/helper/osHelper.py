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

# pylint: disable=maybe-no-member,no-member

import pkgutil

import tortuga.helper
from tortuga.objects import osInfo
from tortuga.objects import osFamilyInfo
from tortuga.os_utility import osUtility
from tortuga.exceptions.osNotSupported import OsNotSupported
from tortuga.helper.osConfigBase import OSConfigBase


def find_subclasses(cls):
    """
    Find all subclass of cls in py files located in subdirectory 'path'
    """

    subclasses = []

    def look_for_subclass(modulename):
        module = __import__(modulename)

        # Walk the dictionaries to get to the last one
        d = module.__dict__
        for m in modulename.split('.')[1:]:
            d = d[m].__dict__

        # Search dictionary for subclasses of 'cls'
        for key, entry in d.items():
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    subclasses.append(entry)
            except TypeError:
                # This happens when a non-type is passed to issubclass. We
                # don't care as it can't be a subclass of cls if it isn't
                # a type
                continue

    for _, name, _ in pkgutil.iter_modules(path=tortuga.helper.__path__,
                                           prefix='tortuga.helper.'):
        look_for_subclass(name)

    return subclasses


def getOsConfigClass(name):
    osConfigClass = None

    for osConfigClass in find_subclasses(OSConfigBase):
        if osConfigClass.is_supported(name):
            break
    else:
        raise OsNotSupported('Operating system [%s] not supported' % (name))

    return osConfigClass


def getOsInfo(osName=None, osVersion=None, osArch=None):
    if osName is not None:
        osConfigClass = getOsConfigClass(osName)

        osconfig = osConfigClass(osName, osVersion, osArch)
    else:
        nativeOsInfo = osUtility.getNativeOsInfo()

        osConfigClass = getOsConfigClass(nativeOsInfo.getName())

        osconfig = osConfigClass(nativeOsInfo.getName(),
                                 nativeOsInfo.getVersion(),
                                 nativeOsInfo.getArch())

    _osInfo = osInfo.OsInfo(osconfig.name, osconfig.vers, osconfig.arch)

    _osFamilyInfo = osFamilyInfo.OsFamilyInfo(
        osconfig.family, osconfig.familyvers, osconfig.arch)

    _osInfo.setOsFamilyInfo(_osFamilyInfo)

    return _osInfo
