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

import platform
import os
import shutil

from tortuga.objects.osInfo import OsInfo
from tortuga.exceptions.unsupportedOperatingSystem \
    import UnsupportedOperatingSystem
from tortuga.exceptions.fileNotFound import FileNotFound
from tortuga.exceptions.osNotSupported import OsNotSupported
from tortuga.os_utility import tortugaSubprocess


def getOsObjectFactory(osName=None):
    if not osName:
        osName = getNativeOsFamilyInfo().getName()

    factoryModule = 'tortuga.os_utility.%sObjectFactory' % osName
    factoryClass = '%sObjectFactory' % osName.capitalize()

    try:
        m = __import__(factoryModule, fromlist=[factoryClass])

        return m.__dict__[factoryClass]()
    except ImportError as ex:
        raise UnsupportedOperatingSystem(
            'Unsupported OS: %s (Error: %s)' % (osName, ex))


def mapOsName(osName):
    """ Maps os platform names into standardized versions. """
    osMap = {
        'redhat': 'rhel',
        'centos': 'rhel',
        'oracle': 'rhel',
    }
    key = osName.lower()
    return osMap.get(key, osName.lower())


RHEL = 'rhel'
CENTOS = 'centos'
ORACLE = 'oracle'


def _identify_rhel_variant():
    cmd = '/opt/puppetlabs/bin/facter operatingsystem'

    p = tortugaSubprocess.TortugaSubprocess(cmd)
    stdout, stderr = p.communicate()

    if p.returncode != 0:
        raise OsNotSupported(
            'Unable to determine OS type: stderr=[%s]' % (stderr))

    facterOperatingSystem = stdout.decode().rstrip().lower()

    if facterOperatingSystem == 'redhat':
        name = RHEL
    elif facterOperatingSystem == 'centos':
        name = CENTOS
    elif facterOperatingSystem == 'oraclelinux':
        name = ORACLE
    else:
        raise OsNotSupported(
            'Unsupported OS [%s]' % (facterOperatingSystem))

    return name


def getPlatformOsInfo(flag=False):
    """
    Return the platform specific OS information... typically the native
    call is desired.
    """

    # (osName, osVersion, osDesc) = platform.dist()
    vals = platform.dist()

    osName = vals[0]
    osVersion = vals[1]

    # Check for multiple periods in version
    version_vals = osVersion.split('.')
    if len(version_vals) >= 2:
        osVersion = version_vals[0] + '.' + version_vals[1]

    osArch = platform.machine()

    if osArch in ['i486', 'i586', 'i686', 'i786']:
        osArch = 'i386'

    if not osName:
        vals = platform.uname()

        # (osName, hostName, osVersion, release, machine,
        #  osArch) = platform.uname()

        osName = vals[0].lower()

    if flag:
        if osName == 'redhat':
            osName = _identify_rhel_variant()
    else:
        osName = mapOsName(osName)

    return OsInfo(osName, osVersion, osArch)


def getNativeOsFamilyInfo():
    """ Get native os info. """
    return getPlatformOsInfo()


def getNativeOsInfo():
    return getPlatformOsInfo(True)


def isNativeOsInfo(osInfo):
    """ Return true if os is native. """

    nativeOsInfo = getNativeOsFamilyInfo()

    if nativeOsInfo == osInfo:
        return True

    return False


def isNativeOsName(osInfo):
    """ Return true if os name is native. """

    nativeOsInfo = getNativeOsFamilyInfo()

    if mapOsName(nativeOsInfo.getName()) == mapOsName(osInfo.getName()):
        return True

    return False


def createDir(path):
    """ Create directory if it does not exist already. """
    if not os.path.isdir(path):
        os.makedirs(path)


def removeLink(path):
    """ Remove link on a given path. """
    if not os.path.islink(path):
        return

    os.remove(path)


def removeFile(path):
    """ Remove file on a given path. """

    try:
        os.unlink(path)
    except OSError as exc:
        # Silently catch the exception if the file does not exist
        if exc.errno != 2:
            raise


def removeDir(path):
    """ Remove dir on a given path, even if it is not empty. """

    try:
        shutil.rmtree(path)
    except OSError as exc:
        # Silently catch the exception if the directory does not exist
        if exc.errno != 2:
            raise


def findFiles(dirPath, fileList=None):
    """ List files in a given directory. Return list of absolute paths.
    Do not follow symbolic links.
    """
    fList = fileList
    if not fList:
        fList = []
    if os.path.isdir(dirPath):
        files = os.listdir(dirPath)
        for f in files:
            fullPath = os.path.join(dirPath, f)
            if os.path.isfile(fullPath):
                fList.append(fullPath)
            elif os.path.isdir(fullPath):
                fList = findFiles(fullPath, fList)
    return fList


def cpio_copytree(src, dst):
    """
    A cpio-based copytree functionality. Only use this when
    shutil.copytree don't cut it.
    """

    # convert paths to be absolute
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    if not os.path.exists(src):
        raise FileNotFound("Source directory does not exist!")

    createDir(dst)

    return os.system('cpio-helper.sh %s %s' % (src, dst))


def make_symlink_farm(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    srclen = len(src)
    for root, _, files in os.walk(src, followlinks=True):
        newdir = dst + root[srclen:]

        if not os.path.exists(newdir):
            os.makedirs(newdir)

        for f in files:
            target = '%s/%s' % (root, f)
            link = '%s/%s' % (newdir, f)

            if not os.path.lexists(link):
                os.symlink(target, link)


BACKUP_FILE_SUFFIX = '.UCBAK'


def __getBackupFileName(filePath):
    if filePath is None:
        raise FileNotFound('Invalid path specified')

    return '%s%s' % (filePath, BACKUP_FILE_SUFFIX)


def __getFileNameFromBackup(filePath):
    if filePath is None:
        raise FileNotFound('Invalid path specified')

    return filePath.rsplit(BACKUP_FILE_SUFFIX, 1)[0]


def backupFile(filePath):
    backupFilePath = __getBackupFileName(filePath)

    if not os.path.exists(filePath):
        raise FileNotFound('Path %s does not exist' % filePath)

    shutil.copy(filePath, backupFilePath)


def restoreFile(filePath):
    backupFilePath = __getBackupFileName(filePath)

    if not os.path.exists(backupFilePath):
        raise FileNotFound('Backup file for %s doe not exist' % filePath)

    shutil.move(backupFilePath, filePath)


def haveBackupFile(filePath):
    backupFilePath = __getBackupFileName(filePath)

    return os.path.exists(backupFilePath)
