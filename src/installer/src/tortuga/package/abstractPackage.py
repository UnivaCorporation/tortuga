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

# pylint: disable=no-self-use

from tortuga.exceptions.abstractMethod import AbstractMethod


class AbstractPackage(object):
    def get_package_license(self, pkgFile): \
            # pylint: disable=unused-argument
        raise AbstractMethod('get_package_license')

    def get_rpm_license_files(self, pkgFile): \
            # pylint: disable=unused-argument
        raise AbstractMethod('get_rpm_license_files')

    def extract_license_file(self, pkgFile, path, license_fulldir, txtfile): \
            # pylint: disable=unused-argument
        raise AbstractMethod('extract_license_file')
