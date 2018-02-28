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

# pylint: disable=no-member,maybe-no-member

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.componentNotFound import ComponentNotFound
from tortuga.kit import kitApiFactory


class KitCli(TortugaCli):
    """
    Base kit command line interface class.
    """

    def get_name_version_iteration(self):
        if self._args:
            pkgname = self._args[0]
            a = pkgname.split('-')
            name = a[0]
            version = '-'.join(a[1:-1])
            iteration = a[-1]
        else:
            name = self.getOptions().name
            version = self.getOptions().version
            iteration = self.getOptions().iteration

        return name, version, iteration

    def getKitNameVersionIteration(self, pkgname):
        if pkgname:
            a = pkgname.split('-')
            name = a[0]
            version = '-'.join(a[1:-1])
            iteration = a[-1]
        else:
            name = self.getOptions().kitName
            version = self.getOptions().kitVersion
            iteration = self.getOptions().kitIteration

        return name, version, iteration

    def getComponent(self, kitName, kitVersion, kitIteration, compdescr): \
            # pylint: disable=no-self-use
        """
        Get Component matching 'compdescr' from specified kit

        Raises:
            ComponentNotFound
        """

        kitApi = kitApiFactory.getKitApi()

        k = kitApi.getKit(kitName, kitVersion, kitIteration)

        c = None

        for c in k.getComponentList():
            _compDescr = '%s-%s' % (c.getName(), c.getVersion())

            if _compDescr == compdescr:
                break
        else:
            raise ComponentNotFound(
                'Component [%s] not found in kit [%s]' % (compdescr, k))

        return c
