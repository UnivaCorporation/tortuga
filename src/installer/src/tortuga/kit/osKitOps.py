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
Base class for OS kit 'plugins'
"""

import logging
import os
from typing import Dict

from tortuga.boot.distro import DistributionFactory
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.abstractMethod import AbstractMethod
from tortuga.logging import KIT_NAMESPACE
from tortuga.os_utility.osUtility import getOsObjectFactory


class OsKitOps(object):
    def __init__(self, osdistro: DistributionFactory, **kwargs):
        self._osdistro: DistributionFactory = osdistro

        self._kit = None

        self._bInteractive = kwargs['bInteractive'] \
            if 'bInteractive' in kwargs else False

        self._bUseSymlinks = kwargs['bUseSymlinks'] \
            if 'bUseSymlinks' in kwargs else False

        self._mirror = kwargs['mirror'] if 'mirror' in kwargs else False

        self._logger = logging.getLogger(KIT_NAMESPACE)

        self._cm = ConfigManager()

        self.pxeboot_dir = os.path.join(
            getOsObjectFactory().getOsBootHostManager(self._cm).getTftproot(),
            'tortuga')

    @property
    def logger(self):
        return self._logger

    @property
    def osdistro(self):
        return self._osdistro

    @property
    def mirror(self):
        """
        Returns bool indicating if specified OS kit is an OS distribution
        mirror
        """

        return self._mirror

    @property
    def kit(self):
        return self._kit

    @kit.setter
    def kit(self, value):
        self._kit = value

    def copyOsMedia(self) -> None:
        raise AbstractMethod('copyOsMedia() is an abstract method')

    def prepareOSKit(self) -> Dict[str, str]:
        raise AbstractMethod('prepareOSKit() is an abstract method')
