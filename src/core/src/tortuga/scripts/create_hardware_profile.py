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
from optparse import OptionValueError

from jinja2 import Template

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.invalidProfileCreationTemplate \
    import InvalidProfileCreationTemplate
from tortuga.objects.hardwareProfile import HardwareProfile
from tortuga.objects.osInfo import OsInfo
from tortuga.softwareprofile.softwareProfileFactory \
    import getSoftwareProfileApi
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class CreateHardwareProfileCli(TortugaCli):
    def __init__(self):
        super().__init__()

        self._default_tmpl_dir = os.path.join(
            ConfigManager().getRoot(),
            'share/templates/hardware')

        # Set up some defaults
        #   Don't need user info here...this is an open api...

        primaryInstallerSp = \
            getSoftwareProfileApi().getSoftwareProfileById(1)

        self.osInfo = primaryInstallerSp.getOsInfo()

        self.defaultOs = '%s-%s-%s' % (self.osInfo.getName(),
                                       self.osInfo.getVersion(),
                                       self.osInfo.getArch())

        self.tmplDict = {}

        option_group_name = _('Information')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--list-templates',
                              action='store_true',
                              dest='bDisplayTemplateList',
                              default=False,
                              help=_('List available hardware profile'
                                     ' templates'))

        option_group_name = _('Create Hardware Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '-x', '--xml-file',
                              dest='templatePath',
                              help=_('Path to hardware profile creation'
                                     ' template'))

        self.addOptionToGroup(
            option_group_name, '-j', '--json-file', dest='jsonTemplatePath',
            help=_('Path to JSON-formatted hardware profile creation'
                   ' template'))

        self.addOptionToGroup(option_group_name, '--name', type='str',
                              action='callback', callback=self.optCallback,
                              help=_('Hardware profile name'))
        self.addOptionToGroup(option_group_name, '--description',
                              action='callback', callback=self.optCallback,
                              type='str', dest='description',
                              help=_('Description for hardware profile'))
        self.addOptionToGroup(option_group_name, '--os', action='callback',
                              metavar='OS SPEC', default=self.defaultOs,
                              callback=self.optCallback, type="str", dest='os',
                              help=_('Operating system (default: %default)'))
        self.addOptionToGroup(option_group_name, '--idleSoftwareProfile',
                              type='str', dest='idleSoftwareProfile',
                              action='callback', callback=self.optCallback,
                              help=_('Specify idle software profile'))

        self.addOptionToGroup(option_group_name, '--defaults',
                              dest='bUseDefaults', default=False,
                              action='store_true',
                              help=_('Do not use any defaults when'
                                     ' creating the hardware profile'))

    def optCallback(self, option, opt, value, parser): \
            # pylint: disable=unused-argument
        _optname = opt[2:]
        _value = value

        if _optname == 'os':
            osValues = _value.split('-', 3)
            if len(osValues) != 3:
                raise InvalidCliRequest(
                    _('Error: Incorrect operating system'
                      ' specification.\n\n'
                      '--os argument should be in NAME-VERSION-ARCH'
                      ' format'))
            name = osValues[0]
            version = osValues[1]
            arch = osValues[2]
            self.osInfo = OsInfo(name, version, arch)
            return

        self.tmplDict[_optname] = _value

    def displayTemplateList(self): \
            # pylint: disable=no-self-use
        templateFiles = glob.glob(
            os.path.join(self._default_tmpl_dir, '*.xml'))

        if templateFiles:
            print('\n'.join(templateFiles))

    def runCommand(self):
        self.parseArgs(_("""
    create-hardware-profile --list-templates

    create-hardware-profile --xml-file TEMPLATEPATH --name=NAME
       [ --description=DESCRIPTION ] [ --os=OS ] [ --idle=SOFTWAREPROFILENAME ]

Description:
    The  create-hardware-profile  tool either lists the paths of available
    templates or creates a hardware profile from  an  existing  template.
    When  creating a hardware profile the description, os, and idle soft-
    ware profile specified in the template can be overridden by providing
    the appropriate command line options.
"""))

        if self.getOptions().bDisplayTemplateList:
            self.displayTemplateList()
            return

        if self.getOptions().templatePath and \
                self.getOptions().jsonTemplatePath:
            raise OptionValueError(
                _('Only one hardware profile template can be specified'))

        template_path = self.getOptions().templatePath \
            if self.getOptions().templatePath else \
            self.getOptions().jsonTemplatePath

        b_use_default_template = False
        if not template_path:
            template_path = os.path.join(
                self._default_tmpl_dir, 'defaultHardwareProfile.tmpl.xml')

            b_use_default_template = True

        if not os.path.exists(template_path):
            raise InvalidCliRequest(
                _('Cannot read template from %s') % (
                    self.getOptions().templatePath))

        settings_dict = {
            'bUseDefaults': self.getOptions().bUseDefaults,
            'osInfo': self.osInfo,
        }

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        try:
            # Process the hardware profile template
            with open(template_path) as fp:
                tmpl = fp.read()

            hw_profile_tmpl = Template(tmpl).render(self.tmplDict)
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

            if b_use_default_template or self.getOptions().templatePath:
                hw_profile_spec = HardwareProfile.getFromXml(
                    hw_profile_tmpl, ['id', 'hardwareProfileId'])
            else:
                hw_profile_dict = json.loads(hw_profile_tmpl)

                hw_profile_spec = HardwareProfile.getFromDict(
                    hw_profile_dict['hardwareProfile'])

            # Override any preset hardware profile name in the template
            # if specified on the command-line
            if 'name' in self.tmplDict:
                hw_profile_spec.setName(self.tmplDict['name'])
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
