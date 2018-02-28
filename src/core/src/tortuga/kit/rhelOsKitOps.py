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

from tortuga.boot.bootMediaTool import BootMediaTool
from tortuga.os_utility.osUtility \
    import cpio_copytree, removeFile, make_symlink_farm
from tortuga.kit.osKitOps import OsKitOps
from tortuga.exceptions.copyError import CopyError
from tortuga.exceptions.fileAlreadyExists import FileAlreadyExists
from tortuga.exceptions.unrecognizedKitMedia import UnrecognizedKitMedia
from tortuga.kit.manager import KitManager
from tortuga.kit.utils import format_kit_descriptor


class KitOps(OsKitOps):
    def prepareOSKit(self, srcPath):
        version = self.osdistro.version \
            if not self.mirror else self.osdistro.version.split('.', 1)[0]

        kit = {
            'ver': version,
            'arch': self.osdistro.arch,
            'name': self.osdistro.ostype,
        }

        kit_descr = format_kit_descriptor(kit['name'], kit['ver'], kit['arch'])

        kit['sum'] = 'OS kit for %s %s' % (kit['name'], kit['ver'])
        kit['initrd'] = 'initrd-%s.img' % (kit_descr)
        kit['kernel'] = 'kernel-%s' % (kit_descr)

        # Copy kernel & initrd to pxedir
        if not os.path.exists(self.pxeboot_dir):
            os.makedirs(self.pxeboot_dir)

        bmt = BootMediaTool(srcPath)

        # Check whether this is disc 1.
        if bmt.getKernelPath() is None or bmt.getInitrdPath() is None:
            raise UnrecognizedKitMedia("Please supply disc 1 first!")

        try:
            bmt.copyInitrd(os.path.join(self.pxeboot_dir, kit['initrd']), True)

            # copy kernel to standardized name
            bmt.copyKernel(os.path.join(self.pxeboot_dir, kit['kernel']), True)
        except (CopyError, FileAlreadyExists, IOError) as exc:
            # cleanup tmp stuff

            self.logger.error(
                'Error copying initrd and/or kernel from OS media'
                ' (exception=[%s])' % (exc))

            # consider the kernel/initrd invalidated, remove them
            removeFile(os.path.join(self.pxeboot_dir, kit['kernel']))
            removeFile(os.path.join(self.pxeboot_dir, kit['initrd']))

            raise

        self.kit = kit

        return kit

    def _getRepoDir(self):
        return self._cm.getYumKit(
            self._osdistro.ostype.lower(),
            self._osdistro.getVersion(),
            self._osdistro.getArch())

    def copyOsMedia(self, srcPath, **kwargs):
        dstPath = self._getRepoDir()

        if 'descr' in kwargs and kwargs['descr']:
            print('Please wait... %s' % (kwargs['descr']))

        if self._bUseSymlinks:
            make_symlink_farm(srcPath, dstPath)
        else:
            cpio_copytree(srcPath, dstPath)

    def addProxy(self, url):
        self._logger.info('Proxy OS kit detected, no RPMs will be copied')

        # Determine the "real" repo dir and the directory as apache
        # sees it

        realRepoDir = self._getRepoDir()

        repoDir = realRepoDir[realRepoDir.index('/repos'):]

        # Set proxy information in the apache component configuration file
        self._logger.info(
            'Enabling proxy for OS kit in web server configuration file')

        # Configure proxy
        KitManager().configureProxy(url, repoDir)
