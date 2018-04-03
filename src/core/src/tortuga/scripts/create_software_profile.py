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
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.invalidProfileCreationTemplate \
    import InvalidProfileCreationTemplate
from tortuga.objects.osInfo import OsInfo
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class CreateSoftwareProfileCli(TortugaCli):
    def __init__(self):
        super().__init__()

        self._default_tmpl_dir = os.path.join(
            self._cm.getRoot(), 'share/templates/software')

        self.osInfo = None

        self.tmplDict = {}

        option_group_name = _('Information')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--list-templates',
                              action='store_true',
                              dest='bDisplayTemplateList',
                              default=False,
                              help=_('List available software profile'
                                     ' templates'))

        # Add options group and options specific to creation of a software
        # profile
        option_group_name = _('Create Software Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '-x', '--xml-file',
                              dest='templatePath',
                              help=_('Path to software profile creation'
                                     ' template'))

        self.addOptionToGroup(
            option_group_name, '-j', '--json-file', dest='jsonTemplatePath',
            help=_('Path to JSON-formatted software profile creation'
                   ' template'))

        self.addOptionToGroup(option_group_name, '--name', action='callback',
                              callback=self.optCallback, type="str",
                              help=_('Software profile name'))
        self.addOptionToGroup(option_group_name, '--description',
                              action='callback', callback=self.optCallback,
                              type="str", dest='description',
                              help=_('Description for software profile'))
        self.addOptionToGroup(option_group_name, '--type', action='callback',
                              callback=self.optCallback, type='str',
                              dest='profileType',
                              help=_('Software profile type'))
        self.addOptionToGroup(option_group_name, '--os', action='callback',
                              metavar='OS SPEC',
                              callback=self.optCallback, type="str", dest='os',
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

    def displayTemplateList(self):
        filespec = os.path.join(self._default_tmpl_dir, '*.xml')

        templateFiles = glob.glob(filespec)

        if templateFiles:
            print('\n'.join(templateFiles))

    def optCallback(self, option, opt, value, parser): \
            # pylint: disable=unused-argument
        _optname = opt[2:]

        if _optname == 'os':
            osValues = value.split('-', 3)

            if len(osValues) != 3:
                raise InvalidCliRequest(
                    _('Error: Incorrect operating system specification.'
                      '\n\n--os argument should be in'
                      ' OSNAME-OSVERSION-OSARCH format'))

            name = osValues[0]
            version = osValues[1]
            arch = osValues[2]

            self.osInfo = OsInfo(name, version, arch)

        self.tmplDict[_optname] = value

    def runCommand(self):
        self.parseArgs(_("""
    create-software-profile --list-templates

    create-software-profile --xml-file TEMPLATEPATH --name=NAME
       [--description=DESCRIPTION] [--os=OS] [--type=TYPE] [--unmanaged]

Description:
    The  create-software-profile  tool either lists the paths of available
    templates or creates a software profile from  an  existing  template.

    When creating a software profile the description, os, and type speci-
    fied in the template can be overridden by providing  the  appropriate
    command line options.
"""))

        if self.getOptions().bDisplayTemplateList:
            self.displayTemplateList()
            return

        if self.getOptions().templatePath and \
                self.getOptions().jsonTemplatePath:
            raise OptionValueError(
                _('Only one software profile template can be specified'))

        template_path = self.getOptions().templatePath \
            if self.getOptions().templatePath else \
            self.getOptions().jsonTemplatePath

        b_use_default_template = False

        if not template_path:
            # Attempt to use default template
            template_path = os.path.join(
                self._default_tmpl_dir, 'defaultSoftwareProfile.tmpl.xml')

            b_use_default_template = True

        if not os.path.exists(template_path):
            raise InvalidCliRequest(
                _('Cannot read template from %s') % (template_path))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        # Populate 'settings_dict' from command-line arguments
        settings_dict = {
            'bOsMediaRequired': self.getOptions().bOsMediaRequired,
            'unmanagedProfile': self.getOptions().unmanaged,
        }

        try:
            with open(template_path) as fp:
                temp_ = fp.read()

            # Process the XML template
            tmpl = Template(temp_).render(self.tmplDict)
        except Exception as ex:
            self.getLogger().debug('Error applying template substitutions')

            self.getLogger().exception(ex)

            raise InvalidProfileCreationTemplate(
                'Invalid profile creation template: %s' % (ex))

        try:
            if b_use_default_template or self.getOptions().templatePath:
                # We want to ignore all tags with id and software profile
                # id...they would be there if the template was created from
                # a dump of an existing profile

                sw_profile_spec = SoftwareProfile.getFromXml(
                    tmpl, ['id', 'softwareProfileId'])
            else:
                sw_profile_dict = json.loads(tmpl)

                sw_profile_spec = SoftwareProfile.getFromDict(
                    sw_profile_dict['softwareProfile'])
        except Exception as ex:
            self.getLogger().debug('Error parsing XML template')
            self.getLogger().exception(ex)
            raise InvalidProfileCreationTemplate(
                'Invalid profile creation template')

        if not sw_profile_spec:
            raise InvalidProfileCreationTemplate(
                'Invalid software creation template')

        if self.osInfo:
            sw_profile_spec.setOsInfo(self.osInfo)

        api.createSoftwareProfile(
            sw_profile_spec, settings_dict)


def main():
    CreateSoftwareProfileCli().run()
