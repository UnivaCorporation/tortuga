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

"""
MountManager

Simple class for mounting/umounting specified media

This code originally extracted from kitops
"""

import logging
import os
import subprocess
import tempfile

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.cannotMountKitMedia import CannotMountKitMedia
from tortuga.logging import KITS_NAMESPACE


class MountManager(object):
    def __init__(self, media):
        self._media = media
        self._mountpoint = ''
        self.bIsMounted = False
        self._tmpprefix = '/tmp'
        self.bIsIso = False
        self._logger = logging.getLogger(KITS_NAMESPACE)

        self._cm = ConfigManager()

    def __repr__(self):
        if not self.bIsMounted:
            return '<MountManager(<UNMOUNTED>)>'

        return '<MountManager([%s] mounted on [%s])>' % (
            self._media, self.mountpoint)

    @property
    def mountpoint(self):
        return self._mountpoint

    @mountpoint.setter
    def mountpoint(self, mountpoint):
        self._mountpoint = mountpoint

    def isMounted(self):
        return self.bIsMounted

    def mountMedia(self):
        """
        Mount the specified media to a temporary directory.
        """

        self.bIsIso = os.path.isfile(self._media)

        tmpmntdir = tempfile.mkdtemp(prefix='kitops', dir=self._tmpprefix)

        if not os.path.exists(self._media):
            raise CannotMountKitMedia('Media [%s] not found' % (
                self._media))

        if self.bIsIso:
            cmd = ['mount', '-ro', 'loop']
        else:
            cmd = ['mount']

        cmd += [self._media, tmpmntdir]

        mountError = self._domount(cmd)

        if mountError:
            os.rmdir(tmpmntdir)

            self._logger.error('Mount fail error: %s' % (mountError))

            raise CannotMountKitMedia(exception=mountError)

        self.mountpoint = tmpmntdir
        self.bIsMounted = True

    def _domount(self, cmd):
        mountP = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        out, err = mountP.communicate()

        if mountP.returncode != 0:
            self._logger.debug('Mount stdout: %s', out)
            self._logger.debug('Mount stderr: %s', err)
            errors = self.__handleMountError(mountP.returncode)
            mountError = 'Mount error(s) %d: %s' % (
                mountP.returncode, ', '.join(errors)) + '\n%s' % (err)

            return mountError

        return None

    def unmountMedia(self):
        """
        self.mountpoint is unmounted, removed and set to None.
        """

        if self.isMounted() and \
           self.mountpoint and \
           os.path.ismount(self.mountpoint):
            cmd = ['umount', self.mountpoint]

            umountP = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            umountP.communicate()

            if umountP.returncode == 0:
                os.rmdir(self.mountpoint)

                self.bIsMounted = False

                self.mountpoint = None
            else:
                self._logger.error(
                    'Unable to unmount [%s]' % (self.mountpoint))

    def __handleMountError(self, rv):   # pylint: disable=no-self-use
        '''
        handle the mount exit status when it's non-zero. Return nothing
        '''

        errdict = {
            1: 'incorrect invocation or permissions',
            2: ('system error (out of memory, cannot fork, no more loop'
                ' devices)'),
            4: 'internal mount bug or missing nfs support in mount',
            8: 'user interrupt',
            16: 'problems writing or locking /etc/mtab',
            32: 'generic mount failure',
            64: 'some mount succeeded'
        }

        errors = []

        for key in errdict:
            if rv & key:
                errors.append(errdict[key])

        return errors
