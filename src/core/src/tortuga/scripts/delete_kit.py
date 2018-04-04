#!/usr/bin/env python

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

from tortuga.kit.kitCli import KitCli
from tortuga.wsapi.kitWsApi import KitWsApi


class DeleteKitCli(KitCli):
    """
    Delete kit command line interface.

    """
    def __init__(self):
        super().__init__()

        kit_attr_group = _('Kit Attribute Options')

        self.addOptionGroup(
            kit_attr_group, _('Kit name/version must be specified.'))

        self.addOptionToGroup(
            kit_attr_group, '--name', dest='name', help=_('kit name'))

        self.addOptionToGroup(
            kit_attr_group, '--version', dest='version', help=_('kit version'))

        self.addOptionToGroup(
            kit_attr_group, '--iteration', dest='iteration',
            help=_('kit iteration'))

        options_attr_group = _('Options')

        self.addOptionGroup(options_attr_group, '')

        self.addOptionToGroup(options_attr_group, '--force',
                              action='store_true', default=False,
                              help=_('Forcibly remove a kit that may be in'
                                     ' use. Use with care!'))

    def runCommand(self):
        self.parseArgs(_("""
    delete-kit --name=NAME [--version=VERSION --iteration=ITERATION]

Description:
    The  delete-kit tool deletes an installed operating system or application
    kit from Tortuga.

    All components from a kit must be disabled before the kit can be suc-
    cessfully deleted.

    If '--force' is specified, the kit can be removed even if it is currently
    in use (ie. operating system kit associated with a software profile). Use
    '--force' with care!
"""))

        name, version, iteration = self.get_name_version_iteration()

        api = KitWsApi(username=self.getUsername(),
                       password=self.getPassword(),
                       baseurl=self.getUrl())

        api.deleteKit(name, version, iteration, force=self.getArgs().force)


def main():
    DeleteKitCli().run()
