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


class OSConfigBase(object):
    families = {}

    def __init__(self, name=None, vers=None, arch=None):
        self._name = name
        self._vers = vers
        self._arch = arch

    @classmethod
    def is_supported(cls, name):
        return name in cls.families

    @property
    def name(self):
        return self._name

    @property
    def vers(self):
        return self._vers

    @property
    def arch(self):
        return self._arch

    @property
    def family(self):
        if self.name in self.families:
            return self.families[self.name]

        return None

    @property
    def familyvers(self):
        if not self.vers:
            return None

        return self.vers
