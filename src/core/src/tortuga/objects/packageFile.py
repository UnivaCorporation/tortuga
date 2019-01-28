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
from tortuga.objects.tortugaObject import TortugaObject


class PackageFile(TortugaObject): \
        # pylint: disable=too-many-public-methods

    """
    Base package file class.
    """

    ROOT_TAG = 'package'

    def __init__(self, path):
        TortugaObject.__init__(self, {'path': path}, ['path'])

    def getRelativePath(self):
        """ Return package relative path. """
        return self['path']

    def getRelativeDir(self):
        """ Return package relative directory path. """
        return os.path.dirname(self['path'])

    def getFileName(self):
        """ Return package file name. """
        return os.path.basename(self['path'])

    def __repr__(self):
        """ Display info. """
        return self['path']

    @staticmethod
    def getKeys():
        return ['path']
