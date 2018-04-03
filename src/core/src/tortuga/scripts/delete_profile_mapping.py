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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class DeleteProfileMappingCli(TortugaCli):
    """
    Get software uses hardware command line interface.
    """

    def __init__(self):
        super().__init__()

        software_uses_hardware_attr_group = \
            _('Software Uses Hardware Attribute Options')

        self.addOptionGroup(
            software_uses_hardware_attr_group,
            _('Software and hardware profile ID must be specified.'))

        self.addOptionToGroup(
            software_uses_hardware_attr_group, '--software-profile',
            dest='swprofile', metavar='SOFTWAREPROFILENAME',
            help=_('software profile'))

        self.addOptionToGroup(
            software_uses_hardware_attr_group, '--hardware-profile',
            dest='hwprofile', metavar='HARDWAREPROFILENAME',
            help=_('hardware profile'))

    def runCommand(self):
        self.parseArgs(_("""
   delete-profile-mapping  --software-profile=SOFTWAREPROFILENAME --hardware-profile=HARDWAREPROFILENAME

Description:
    The  delete-profile-mapping  tool  adjusts  the  software  uses hardware
    attribute on  a  software  profile.   This  attribute  allows  for  a
    restriciton on what hardware profiles a given software profile can be
    associated with.
"""))

        swprofile_name = self.getOptions().swprofile

        if not swprofile_name:
            raise InvalidCliRequest(
                _('Software profile name must be specified'))

        hwprofile_name = self.getOptions().hwprofile

        if not hwprofile_name:
            raise InvalidCliRequest(
                _('Hardware profile name must be specified'))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.deleteUsableHardwareProfileFromSoftwareProfile(
            hwprofile_name, swprofile_name)


def main():
    DeleteProfileMappingCli().run()
