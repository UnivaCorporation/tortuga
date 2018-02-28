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

from tortuga.package.abstractPackage import AbstractPackage
from tortuga.os_utility.tortugaSubprocess import TortugaSubprocess


class RPM(AbstractPackage):
    def get_package_license(self, pkgFile):  # pylint: disable=no-self-use
        '''
        Returns the packages' license (BSD, GPL, etc...)
        '''

        p = TortugaSubprocess(
            'rpm -qp --queryformat "%%{LICENSE}" %s 2>/dev/null' % (
                pkgFile))

        p.run()

        licensetxt = p.getStdOut()

        return licensetxt

    def get_rpm_license_files(self, pkgFile):  # pylint: disable=no-self-use
        '''
        Returns a list of license files found in the package
        '''

        p = TortugaSubprocess(
            'rpm2cpio %s | cpio -it | grep -e COPYING -e LICENSE || true' % (
                pkgFile))

        p.run()

        a = p.getStdOut().split("\n")

        while a and a[-1] == '':
            a.pop()  # There's always a blank line at the end

        return a

    def extract_license_file(self, pkgFile, path, license_fulldir, txtfile): \
            # pylint: disable=no-self-use
        '''
        Extract it into the license_fulldir, changing all
        slashes to dashes, removing any leading punctuation,
        and adding an extension that makes browsers happy.
        '''

        p = TortugaSubprocess(
            'rpm2cpio %s | cpio -i --to-stdout %s > %s/%s' % (
                pkgFile, path, license_fulldir, txtfile))

        p.run()
