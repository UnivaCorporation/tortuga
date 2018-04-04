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

# pylint: disable=no-member

import glob
import json

import os.path
from jinja2 import Template
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.cli.utils import ParseOperatingSystemArgAction
from tortuga.cli.utils import ParseProfileTemplateArgsAction
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.invalidProfileCreationTemplate \
    import InvalidProfileCreationTemplate
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class CreateHardwareProfileCli(TortugaCli):
    def __init__(self):
        super().__init__()

        self._default_tmpl_dir = os.path.join(
            ConfigManager().getRoot(),
            'share/templates/hardware')

    def parseArgs(self, usage=None):
        optionGroupName = _('Information')
        self.addOptionGroup(optionGroupName, '')
        self.addOptionToGroup(optionGroupName, '--list-templates',
                              action='store_true',
                              dest='bDisplayTemplateList',
                              default=False,
                              help=_('List available hardware profile'
                                     ' templates'))

        option_group_name = _('Create Hardware Profile Options')

        option_group = self.addOptionGroup(option_group_name, '')

        excl_option_group = option_group.add_mutually_exclusive_group()

        excl_option_group.add_argument(
            '-x', '--xml-file', dest='templatePath',
            help=_('Path to hardware profile creation template'))

        excl_option_group.add_argument(
            '-j', '--json-file', dest='jsonTemplatePath',
            help=_('Path to JSON-formatted hardware profile creation'
                   ' template'))

        self.addOptionToGroup(optionGroupName, '--name',
                              action=ParseProfileTemplateArgsAction,
                              help=_('Hardware profile name'))
        self.addOptionToGroup(optionGroupName, '--description',
                              action=ParseProfileTemplateArgsAction,
                              dest='description',
                              help=_('Description for hardware profile'))
        self.addOptionToGroup(optionGroupName, '--os',
                              action=ParseOperatingSystemArgAction,
                              metavar='OS SPEC',
                              dest='os',
                              help=_('Operating system'))
        self.addOptionToGroup(optionGroupName, '--idleSoftwareProfile',
                              dest='idleSoftwareProfile',
                              action=ParseProfileTemplateArgsAction,
                              help=_('Specify idle software profile'))

        self.addOptionToGroup(option_group_name, '--defaults',
                              dest='bUseDefaults', default=False,
                              action='store_true',
                              help=_('Do not use any defaults when'
                                     ' creating the hardware profile'))

        super().parseArgs(usage=usage)

    def displayTemplateList(self): \
            # pylint: disable=no-self-use
        templateFiles = glob.glob(
            os.path.join(self._default_tmpl_dir, '*.xml'))

        if templateFiles:
            print('\n'.join(templateFiles))

    def runCommand(self):
        self.parseArgs(_("""
The create-hardware-profile tool either lists the paths of available
templates or creates a hardware profile from an existing template.
When creating a hardware profile the description, operating system, and idle
software profile specified in the template can be overridden by providing
the appropriate command line options.
"""))

        if self.getArgs().bDisplayTemplateList:
            self.displayTemplateList()
            return

        template_path = self.getArgs().templatePath \
            if self.getArgs().templatePath else \
            self.getArgs().jsonTemplatePath

        b_use_default_template = False
        if not template_path:
            template_path = os.path.join(
                self._default_tmpl_dir, 'defaultHardwareProfile.tmpl.xml')

            b_use_default_template = True

        if not os.path.exists(template_path):
            raise InvalidCliRequest(
                _('Cannot read template from %s') % (
                    self.getArgs().templatePath))

        osInfo = self.getArgs().osInfo if hasattr(self.getArgs(), 'osInfo') else None

        settings_dict = {
            'bUseDefaults': self.getArgs().bUseDefaults,
            'osInfo': osInfo,
        }

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        try:
            # Process the hardware profile template
            with open(template_path) as fp:
                tmpl = fp.read()

            tmplDict = self.getArgs().tmplDict
            hw_profile_tmpl = Template(tmpl).render(tmplDict)
        except Exception as ex:
            self.getLogger().error(
                'Error applying template substitutions')

            self.getLogger().exception(ex)

            raise InvalidProfileCreationTemplate(
                'Invalid hardware profile creation template: %s' % (ex))

        try:
            # We want to ignore all elements with id and hardware profile
            # id...they would be there if the template was created from a
            # dump of an existing profile

            if b_use_default_template or self.getArgs().templatePath:
                hw_profile_spec = HardwareProfile.getFromXml(
                    hw_profile_tmpl, ['id', 'hardwareProfileId'])
            else:
                hw_profile_dict = json.loads(hw_profile_tmpl)

                hw_profile_spec = HardwareProfile.getFromDict(
                    hw_profile_dict['hardwareProfile'])

            # Override any preset hardware profile name in the template
            # if specified on the command-line
            if 'name' in tmplDict:
                hw_profile_spec.setName(tmplDict['name'])
        except ConfigurationError as ex:
            self.getLogger().exception(ex)

            raise InvalidProfileCreationTemplate(
                'Invalid hardware profile creation template: %s' % (ex))
        except Exception as ex:
            self.getLogger().debug(
                'Error parsing hardware profile template')

            self.getLogger().exception(ex)

            raise InvalidProfileCreationTemplate(
                'Invalid hardware profile creation template')

        if hw_profile_spec is None:
            raise InvalidProfileCreationTemplate(
                'Invalid hardware creation template')

        if not hw_profile_spec.getDescription():
            hw_profile_spec.setDescription('{0} hardware profile'.format(
                hw_profile_spec.getName()))

        api.createHardwareProfile(hw_profile_spec, settings_dict)


def main():
    CreateHardwareProfileCli().run()
