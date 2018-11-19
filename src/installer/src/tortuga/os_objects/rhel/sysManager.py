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

# pylint: disable=no-member

import os

from tortuga.os_objects.osObjectManager import OsObjectManager


class SysManager(OsObjectManager):
    TIME = '/etc/sysconfig/clock'
    KEYBOARD = '/etc/sysconfig/keyboard'
    I18N = '/etc/sysconfig/i18n'

    def findTimeInfo(self):
        """
        Returns tuple containing timezone and utc flag
        """

        timezone = 'America/New_York'
        utc = False

        if not os.path.exists(self.TIME):
            return timezone, utc

        with open(self.TIME) as fp:
            for line in fp.readlines():
                if line[0] == "#":
                    continue

                try:
                    key, _val = line.rstrip().split('=', 1)
                except ValueError:
                    # Ignore any malformed entries
                    continue

                val = _val.replace('"', '')

                if key == 'ZONE':
                    timezone = val
                elif key == 'UTC':
                    utc = (val.lower() in ['true', 'yes'])

        return timezone, utc

    def findKeyboard(self):
        # For safety's sake, ensure there's a sane default
        keyboard = 'us'
        if not os.path.exists(self.KEYBOARD):
            return keyboard
        fin = open(self.KEYBOARD, 'r')
        lines = fin.readlines()
        fin.close()
        for line in lines:
            if line[0] == "#":
                continue
            try:
                key, val = line.rstrip().split('=', 1)
            except ValueError:
                # Ignore malformed entries
                continue

            if key == 'KEYTABLE':
                keyboard = val.lstrip('"').rstrip('"')

        return keyboard

    def findLanguage(self):
        language = ''
        if not os.path.exists(self.I18N):
            return language
        fin = open(self.I18N, 'r')
        lines = fin.readlines()
        fin.close()
        for line in lines:
            if line[0] == "#":
                continue
            try:
                key, val = line.rstrip().split('=', 1)
            except ValueError:
                # Ignore malformed entries
                continue

            if key == 'LANG':
                language = val.lstrip('"').rstrip('"')

                # This may need some additional processing after...

        return language

    def getKernel(self, osInfo): \
            # pylint: disable=no-self-use
        return 'kernel-%s-%s-%s' % (
            osInfo.getName(), osInfo.getVersion(), osInfo.getArch())

    def getInitrd(self, osInfo): \
            # pylint: disable=no-self-use
        return 'initrd-%s-%s-%s.img' % (
            osInfo.getName(), osInfo.getVersion(), osInfo.getArch())

    def getTarCommand(self): \
            # pylint: disable=no-self-use
        """
        Return the GNU tar command.
        """
        return 'tar'
