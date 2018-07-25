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

# pylint: disable=no-member

import argparse
import json
import os.path

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.cli.utils import ParseOperatingSystemArgAction
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.invalidProfileCreationTemplate import \
    InvalidProfileCreationTemplate
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class CreateSoftwareProfileCli(TortugaCli):
    def parseArgs(self, usage=None):
        # Add options group and options specific to creation of a software
        # profile
        option_group_name = _('Create Software Profile Options')
        option_group = self.addOptionGroup(option_group_name, '')

        self.addOptionToGroup(option_group_name,
                              '-j', '--json-file', dest='jsonTemplatePath',
                              help=argparse.SUPPRESS)

        self.addOptionToGroup(option_group_name,
                              '--template', dest='jsonTemplatePath',
                              metavar='PATH',
                              help=_('Path to JSON-formatted software profile'
                                     ' creation template'))

        self.addOptionToGroup(option_group_name, '--name',
                              help=_('Software profile name'))

        self.addOptionToGroup(option_group_name, '--description',
                              dest='description',
                              help=_('Description for software profile'))

        self.addOptionToGroup(option_group_name, '--type',
                              dest='profileType',
                              help=_('Software profile type'))

        self.addOptionToGroup(option_group_name, '--os',
                              action=ParseOperatingSystemArgAction,
                              metavar='OS SPEC',
                              dest='os',
                              help=_('Operating system for software profile'
                                     ' nodes'))

        self.addOptionToGroup(
            option_group_name, '--os-media-required', action='store_true',
            dest='bOsMediaRequired', default=True,
            help=_('OS media required for nodes in this software profile'
                   ' (default)')
        )

        self.addOptionToGroup(
            option_group_name, '--no-os-media-required', action='store_false',
            dest='bOsMediaRequired', default=True,
            help=_('OS media required for nodes in this software profile')
        )

        self.addOptionToGroup(
            option_group_name, '--unmanaged', action='store_true',
            dest='unmanaged',
            help=_('Create an unmanaged software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Create software profile'))

        # load template if specified with '--template', otherwise build
        # template
        tmpl_dict = {} if not self.getArgs().jsonTemplatePath else \
            self.load_software_profile_template(
                self.getArgs().jsonTemplatePath)

        if self.getArgs().name:
            tmpl_dict['name'] = self.getArgs().name

        if self.getArgs().description:
            tmpl_dict['description'] = self.getArgs().description

        if self.getArgs().profileType:
            tmpl_dict['type'] = self.getArgs().profileType
        elif 'type' not in tmpl_dict:
            tmpl_dict['type'] = 'compute'

        if hasattr(self.getArgs(), 'osInfo'):
            tmpl_dict['os'] = {
                'name': getattr(self.getArgs(), 'osInfo').getName(),
                'version': getattr(self.getArgs(), 'osInfo').getVersion(),
                'arch': getattr(self.getArgs(), 'osInfo').getArch(),
            }

        sw_profile_spec = SoftwareProfile.getFromDict(tmpl_dict)

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl(),
                                   verify=self._verify)

        # Populate 'settings_dict' from command-line arguments
        settings_dict = {
            'bOsMediaRequired': self.getArgs().bOsMediaRequired,
            'unmanagedProfile': self.getArgs().unmanaged,
        }

        api.createSoftwareProfile(sw_profile_spec, settings_dict)

    def load_software_profile_template(self, tmplpath: str) -> dict:
        """
        Raises:
            InvalidProfileCreationTemplate
            InvalidCliRequest
        """

        # load from template
        if tmplpath and not os.path.exists(tmplpath):
            raise InvalidCliRequest(
                _('Cannot read software profile template [%s]') % (tmplpath))

        try:
            with open(tmplpath) as fp:
                result = json.load(fp)

                if 'softwareprofile' not in result:
                    raise InvalidProfileCreationTemplate(
                        'Missing \"softwareprofile\" envelope'
                    )

                return result['softwareprofile']
        except Exception as exc:
            raise InvalidProfileCreationTemplate(
                'Invalid software profile template: {}'.format(exc))


def main():
    CreateSoftwareProfileCli().run()


if __name__ == '__main__':
    main()
