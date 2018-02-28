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

from tortuga.boot.distro import DistroFactory
from tortuga.exceptions.copyError import CopyError
from tortuga.exceptions.fileAlreadyExists import FileAlreadyExists


class BootMediaTool(object):
    def __init__(self, srcpath):
        self.srcpath = srcpath
        self.installsrc = DistroFactory(srcpath)

    def validSrcPath(self):
        """ Verify if the srcpath is valid. """
        return self.installsrc.verifySrcPath()

    def getDistro(self):
        """ Returns the OS type. """
        return self.installsrc.ostype

    def getVersion(self):
        """ Returns the OS type. """
        return self.installsrc.getVersion()

    def getKernelPath(self):
        """ Query the srcpath and returns the path of the kernel. """
        return self.installsrc.getKernelPath()

    def getKernelPackages(self):
        """ Returns the list of distro-specific kernel packages. """
        return self.installsrc.getKernelPackages()

    def getInitrdPath(self):
        """ Query the srcpath and returns the path of the initrd. """
        return self.installsrc.getInitrdPath()

    def copyKernel(self, dest, overwrite=False):
        """ Extract the kernel from the srcpath to the dest. A CopyError
            exception will be raised if there are errors when extraction.
        """
        try:
            self.installsrc.copyKernel(dest, overwrite)
        except (CopyError, FileAlreadyExists, IOError) as e:
            raise e

    def copyInitrd(self, dest, overwrite=False):
        """
        Extract the initrd from the srcpath to the dest.

        Raises:
            CopyError
            FileAlreadyExists
            IOError
        """
        try:
            self.installsrc.copyInitrd(dest, overwrite)
        except (CopyError, FileAlreadyExists, IOError) as e:
            raise e
