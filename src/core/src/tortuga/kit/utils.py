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

import filecmp
import json
import logging
import os
import os.path
import shutil
import subprocess
import urllib.error
import urllib.request
from logging import getLogger

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.fileNotFound import FileNotFound
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.os_utility.tortugaSubprocess import TortugaSubprocess

from .metadata import KitMetadataSchema


logger = getLogger(__name__)


def pip_install_requirements(kit_installer, requirements_path):
    """
    Installs packages specified in a requirements.txt file, using the kit
    package repo in addition to the standard python repos. This function
    returns nothing, and does nothing if the requirements.txt file is not
    found.

    :param kit_installer:     an instance of KitInstallerBase, which will
                              be searched for a local python package repo
    :param requirements_path: the path to the requirements.txt file

    """
    #
    # In the kit directory:
    #
    #     /opt/tortuga/kits/kit-x.y.z/tortuga_kits/kit_x_y_z
    #
    # if there is a python_packages directory, with a simple subdirectory
    # in it, it is assumed that the simple subdirectory is a PEP 503
    # compliant Python package repository. If found, this directory is
    # added to the list of directories searched for Python packages via
    # pip when installing the requirements.txt file.
    #
    # These directories can easily be created using the py2pi utility.
    #
    if not os.path.exists(requirements_path):
        logger.debug('Requirements not found: {}'.format(requirements_path))
        return

    if is_requirements_empty(requirements_path):
        logger.debug('Requirements empty: {}'.format(requirements_path))
        return

    pip_cmd = ['{}/pip'.format(ConfigManager().getBinDir()), 'install']

    kit_python_repo = os.path.join(
        kit_installer.install_path,
        'python_packages',
        'simple'
    )
    if os.path.exists(kit_python_repo):
        pip_cmd.extend([
            '--extra-index-url',
            'file://{}'.format(os.path.abspath(kit_python_repo))
        ])

    pip_cmd.extend([
        '-r',
        requirements_path
    ])

    logger.debug(' '.join(pip_cmd))
    subprocess.Popen(pip_cmd).wait()


def is_requirements_empty(requirements_file_path):
    """
    Tests to see if a pip requirements.txt file is empty.

    :param requirements_file_path: the path to the requirements.txt file
    :return:                       True if it is empty, False otherwise

    """
    fp = open(requirements_file_path)
    line_count = 0
    for line in fp.readline():
        line = line.strip()
        #
        # Skip blank lines, or comment lines
        #
        if not line or line.startswith('#'):
            continue
        line_count += 1
    return line_count == 0


def assembleKitUrl(srcUrl, kitFileName):
    """
    Construct kit url.

    """
    if os.path.basename(srcUrl) != kitFileName:
        return '%s/%s' % (srcUrl, kitFileName)

    return srcUrl


def copy(srcFile, destDir):
    """
    :raises FileNotFound:

    """
    logger = logging.getLogger('tortuga.kit.utils')
    logger.addHandler(logging.NullHandler())

    destFile = '%s/%s' % (destDir, os.path.basename(srcFile))

    if os.path.exists(destFile) and filecmp.cmp(srcFile, destFile):
        logger.debug('Files [%s] and [%s] are the same, skipping copy.' % (
            srcFile, destFile))
    else:
        logger.debug('Copying [%s] to [%s]' % (srcFile, destFile))

        try:
            shutil.copy(srcFile, destDir)
        except Exception as ex:
            logger.debug('Copy failed, exception reported: %s' % ex)

            raise FileNotFound('Invalid kit at [%s]' % (srcFile))


def checkSupportedScheme(srcUrl):
    return srcUrl.startswith('http://') or srcUrl.startswith('https://') \
           or srcUrl.startswith('file://') or srcUrl.startswith('ftp://')


def retrieve(kitFileName, srcUrl, destDir):
    """
    :raises FileNotFound:

    """
    if checkSupportedScheme(srcUrl):
        # This is a urllib2 supported url scheme, download kit.
        kitUrl = assembleKitUrl(srcUrl, kitFileName)
        download([kitUrl], destDir)
    elif os.path.isdir(srcUrl):
        kitUrl = assembleKitUrl(srcUrl, kitFileName)
        copy(kitUrl, destDir)
    elif os.path.isfile(srcUrl) and \
            os.path.basename(srcUrl) == kitFileName:
        copy(srcUrl, destDir)
    else:
        raise FileNotFound(
            'File [%s] not found at URL [%s]' % (kitFileName, srcUrl))

    return assembleKitUrl(destDir, kitFileName)


def download(urlList, dest):
    """
    TODO: this should use a curl/wget download module

    """
    logger = logging.getLogger('tortuga.kit.utils')
    logger.addHandler(logging.NullHandler())

    for url in urlList:
        i = url.rfind('/')

        destFile = dest + '/' + url[i + 1:]

        logger.debug(url + '->' + destFile)

        try:
            filein = urllib.request.urlopen(url)
        except urllib.error.URLError as ex:
            if ex.code == 404:
                raise FileNotFound('File not found at URL [%s]' % (url))

            raise TortugaException(exception=ex)
        except Exception as ex:
            raise TortugaException(exception=ex)

        fileout = open(destFile, "wb")

        while True:
            try:
                buf = filein.read(1024000)

                fileout.write(buf)
            except IOError as ex:
                raise TortugaException(exception=ex)

            if not bytes:
                break

        filein.close()
        fileout.close()
        logger.debug('Successfully dowloaded file [%s]' % (destFile))


def getKitNameVersionIteration(kitpath):
    """
    Extract kit name/version/iteration from a kit tarball by parsing
    the enclosed 'kit.json' metadata file.

    :raises KitNotFound:

    """
    cmd = 'tar jxfO {} \*/kit.json'.format(kitpath)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, bufsize=1)

    name = None
    version = None
    iteration = None
    try:
        meta_dict = json.load(p.stdout)
        errors = KitMetadataSchema().validate(meta_dict)
        if not errors:
            name = meta_dict['name']
            version = meta_dict['version']
            iteration = meta_dict['iteration']
    except SyntaxError:
        #
        # This is probably an indication that the kit.json did not exist
        # in the specified tarball.
        #
        pass

    retval = p.wait()
    if retval != 0:
        raise KitNotFound(
            'Unable to parse metadata for kit [{}]'.format(kitpath))

    return name, version, iteration


def unpack(filePath, destrootdir):
    """
    TODO: refactor to use unpack_archive

    :raises InvalidArgument:

    """
    logger = logging.getLogger('tortuga.kit.utils')
    logger.addHandler(logging.NullHandler())

    kit_name, kit_version, kit_iteration = \
        getKitNameVersionIteration(filePath)

    destdir = os.path.join(
        destrootdir,
        'kit-{}'.format(
            format_kit_descriptor(kit_name, kit_version, kit_iteration)
        )
    )

    if not os.path.exists(destdir):
        os.mkdir(destdir)

    logger.debug(
        '[utils.parse()] Unpacking [%s] into [%s]' % (
            filePath, destdir))

    cmd = 'tar --extract --bzip2 --strip-components 1 --file %s -C %s' % (
        filePath, destdir)

    p = TortugaSubprocess(cmd)

    p.run()

    logger.debug(
        '[utils.parse()] Unpacked [%s] into [%s]' % (
            filePath, destdir))

    return destdir


def unpack_archive(kit_archive_path, dest_root_dir):
    """
    :raises InvalidArgument:

    """
    logger = logging.getLogger('tortuga.kit.utils')
    logger.addHandler(logging.NullHandler())

    kit_name, kit_version, kit_iteration = \
        getKitNameVersionIteration(kit_archive_path)

    destdir = os.path.join(
        dest_root_dir,
        'kit-{}'.format(
            format_kit_descriptor(kit_name, kit_version, kit_iteration)
        )
    )

    if not os.path.exists(destdir):
        os.mkdir(destdir)

    logger.debug(
        '[utils.parse()] Unpacking [%s] into [%s]' % (
            kit_archive_path, destdir))

    cmd = 'tar --extract --bzip2 --strip-components 1 --file %s -C %s' % (
        kit_archive_path, destdir)

    p = TortugaSubprocess(cmd)

    p.run()

    logger.debug(
        '[utils.parse()] Unpacked [%s] into [%s]' % (
            kit_archive_path, destdir))

    return kit_name, kit_version, kit_iteration


def format_kit_descriptor(name, version, iteration):
    """
    Returns a properly formatted kit 'descriptor' string in the format
    <name>-<version>-<iteration>

    """
    return '{0}-{1}-{2}'.format(name, version, iteration)


def format_component_descriptor(name, version):
    """
    Return a properly formatted component 'descriptor' in the format
    <name>-<version>

    """
    return '{0}-{1}'.format(name, version)
