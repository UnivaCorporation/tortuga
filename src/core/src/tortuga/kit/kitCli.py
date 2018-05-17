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

from typing import Optional

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.componentNotFound import ComponentNotFound
from tortuga.wsapi.kitWsApi import KitWsApi


class KitCli(TortugaCli):
    """
    Base kit command line interface class.
    """

    def parseArgs(self, usage: Optional[str] = None):
        kit_attr_group = _('Kit Attribute Options')

        self.addOptionGroup(
            kit_attr_group, _('Kit name/version must be specified.'))

        self.addOptionToGroup(
            kit_attr_group, '--name', help=_('kit name'))

        self.addOptionToGroup(
            kit_attr_group, '--version', help=_('kit version'))

        self.addOptionToGroup(
            kit_attr_group, '--iteration', help=_('kit iteration'))

        self.getParser().add_argument('kitspec', nargs='?')

        return super().parseArgs(usage=usage)

    def get_name_version_iteration(self):
        return self.getKitNameVersionIteration(self.getArgs().kitspec)

    def getKitNameVersionIteration(self, pkgname):
        if pkgname:
            a = pkgname.split('-')

            name = a[0]
            version = None
            iteration = None

            if len(a) == 3:
                version = '-'.join(a[1:-1])
                iteration = a[-1]
            elif len(a) == 2:
                version = a[1]
        else:
            name = self.getArgs().name
            version = self.getArgs().version
            iteration = self.getArgs().iteration

        return name, version, iteration

    def getComponent(self, kitName, kitVersion, kitIteration, compdescr): \
            # pylint: disable=no-self-use
        """
        Get Component matching 'compdescr' from specified kit

        Raises:
            ComponentNotFound
        """

        kitApi = KitWsApi(username=self.getUsername(),
                          password=self.getPassword(),
                          baseurl=self.getUrl())

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
