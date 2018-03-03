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
from typing import List, Dict, Any
from tortuga.os_utility.osUtility \
    import cpio_copytree, removeFile, make_symlink_farm
from tortuga.kit.osKitOps import OsKitOps
from tortuga.exceptions.copyError import CopyError
from tortuga.exceptions.fileAlreadyExists import FileAlreadyExists
from tortuga.exceptions.unrecognizedKitMedia import UnrecognizedKitMedia
from tortuga.kit.manager import KitManager


class KitOps(OsKitOps):
    """

    """
    def prepareOSKit(self) -> Dict[str, str]:
        """
        :return: None
        """
        kit: Dict[str, str] = {
            'ver': self.osdistro.version,
            'arch': self.osdistro.architecture,
            'name': self.osdistro.name,
            'sum': 'OS kit for %s %s' % (self.osdistro.name, self.osdistro.version),
            'initrd': self.osdistro.initrd_path,
            'kernel': self.osdistro.kernel_path
        }

        # Copy kernel & initrd to pxedir
        if not os.path.exists(self.pxeboot_dir):
            os.makedirs(self.pxeboot_dir)

        try:
            self.osdistro.copy_initrd(self.pxeboot_dir, True)
            self.osdistro.copy_kernel(self.pxeboot_dir, True)
        except (CopyError, FileAlreadyExists, IOError) as exc:
            self.logger.error(
                'Error copying initrd and/or kernel from OS media'
                ' (exception=[%s])' % exc)

            # consider the kernel/initrd invalidated, remove them
            removeFile(os.path.join(self.pxeboot_dir, kit['kernel']))
            removeFile(os.path.join(self.pxeboot_dir, kit['initrd']))

            raise

        self.kit = kit

        return kit

    def _getRepoDir(self):
        return self._cm.getYumKit(
            self._osdistro.name,
            self._osdistro.version,
            self._osdistro.architecture)

    def copyOsMedia(self, **kwargs: Any) -> None:
        """
        :param kwargs: String
        :return:
        """
        destination_path = self._getRepoDir()

        if 'descr' in kwargs and kwargs['descr']:
            print('Please wait... %s' % (kwargs['descr']))

        if self._bUseSymlinks:
            make_symlink_farm(self.osdistro.source_path, destination_path)
        else:
            cpio_copytree(self.osdistro.source_path, destination_path)

    def addProxy(self, url: str) -> None:
        self._logger.info('Proxy OS kit detected, no RPMs will be copied')

        # Determine the "real" repo dir and the directory as apache
        # sees it

        real_repo_directory: List[str] = self._getRepoDir()

        repo_directory: str = real_repo_directory[real_repo_directory.index('/repos'):]

        # Set proxy information in the apache component configuration file
        self._logger.info(
            'Enabling proxy for OS kit in web server configuration file')

        # Configure proxy
        KitManager().configureProxy(url, repo_directory)
