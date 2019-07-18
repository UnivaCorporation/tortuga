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


import argparse
import json
import os.path
from typing import Optional

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.cli.utils import ParseOperatingSystemArgAction, parse_tags
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.invalidProfileCreationTemplate import \
    InvalidProfileCreationTemplate
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class CreateHardwareProfileCli(TortugaCli):
    def parseArgs(self, usage: Optional[str] = None):
        option_group_name = _('Create Hardware Profile Options')

        self.addOptionGroup(option_group_name, '')

        self.addOptionToGroup(option_group_name, '-j', '--json-file',
                              dest='jsonTemplatePath', help=argparse.SUPPRESS)

        self.addOptionToGroup(option_group_name, '-t', '--template',
                              dest='jsonTemplatePath',
                              help=_('Path to JSON-formatted hardware profile'
                                     ' creation template'))

        self.addOptionToGroup(
            option_group_name, '--name', dest='deprecated_name',
            help=argparse.SUPPRESS
        )

        self.addOptionToGroup(option_group_name, '--description',
                              dest='description',
                              help=_('Hardware profile description'))

        self.addOptionToGroup(option_group_name, '--os',
                              action=ParseOperatingSystemArgAction,
                              metavar='OS SPEC',
                              dest='os',
                              help=_('Hardware profile operating system'))

        self.addOptionToGroup(option_group_name, '--name-format',
                              dest='nameFormat',
                              help=_('Host name format'))

        self.addOptionToGroup(option_group_name, '--tags',
                              dest='tags', metavar='key=value[,key=value]',
                              action='append',
                              help='Key-value pairs associated with the '
                                   'hardware profile')

        self.addOptionToGroup(option_group_name, '--defaults',
                              dest='bUseDefaults', default=False,
                              action='store_true',
                              help=_('Do not use any defaults when'
                                     ' creating the hardware profile'))

        self.getParser().add_argument(
            'name', metavar='NAME', nargs='?', help=_('Hardware profile name')
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        if self.getArgs().name and self.getArgs().deprecated_name:
            self.getParser().error(
                'argument name: not allowed with argument --name'
            )

        name = self.getArgs().name \
            if self.getArgs().name else self.getArgs().deprecated_name

        if self.getArgs().jsonTemplatePath:
            # load from template
            if self.getArgs().jsonTemplatePath and \
                    not os.path.exists(self.getArgs().jsonTemplatePath):
                raise InvalidCliRequest(
                    _('Cannot read template from %s') % (
                        self.getArgs().jsonTemplatePath))

            try:
                with open(self.getArgs().jsonTemplatePath) as fp:
                    buf = json.load(fp)

                tmpl_dict = buf['hardwareProfile']
            except Exception as exc:
                raise InvalidProfileCreationTemplate(
                    'Invalid profile creation template: {}'.format(exc))
        else:
            tmpl_dict = {}

        # build up dict from scratch
        if name:
            tmpl_dict['name'] = name

        if self.getArgs().description:
            tmpl_dict['description'] = self.getArgs().description

        if hasattr(self.getArgs(), 'osInfo'):
            tmpl_dict['os'] = {
                'name': getattr(self.getArgs(), 'osInfo').getName(),
                'version': getattr(self.getArgs(), 'osInfo').getVersion(),
                'arch': getattr(self.getArgs(), 'osInfo').getArch(),
            }

        if self.getArgs().nameFormat:
            tmpl_dict['nameFormat'] = self.getArgs().nameFormat

        elif 'nameFormat' not in tmpl_dict:
            tmpl_dict['nameFormat'] = 'compute-#NN'

        if self.getArgs().tags:
            tmpl_dict['tags'] = parse_tags(self.getArgs().tags)

        settings_dict = {
            'defaults': self.getArgs().bUseDefaults,
            'osInfo': getattr(self.getArgs(), 'osInfo')
            if hasattr(self.getArgs(), 'osInfo') else None,
        }

        hw_profile_spec = HardwareProfile.getFromDict(tmpl_dict)

        api = self.configureClient(HardwareProfileWsApi)
        api.createHardwareProfile(hw_profile_spec, settings_dict)


def main():
    CreateHardwareProfileCli().run()
