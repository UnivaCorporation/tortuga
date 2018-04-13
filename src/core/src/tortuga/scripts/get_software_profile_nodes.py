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


class GetSoftwareProfileNodesCli(TortugaCli):
    """
    Get software profile command line interface.
    """

    def __init__(self):
        super().__init__()

        software_profile_attr_group = _('Software Profile Attribute Options')

        self.addOptionGroup(
            software_profile_attr_group,
            _('Software profile name must be specified.'))

        self.addOptionToGroup(
            software_profile_attr_group,
            '--software-profile',
            metavar='SOFTWAREPROFILENAME',
            dest='softwareProfile',
            help=_('software profile'))

    def runCommand(self):
        self.parseArgs(_("""
    get-software-profile-nodes --software-profile SOFTWAREPROFILENAME

Description:
    The get-software-profile-nodes tool returns the list of nodes that are
    using the specified software profile.
"""))
        software_profile_name = self.getArgs().softwareProfile

        if not software_profile_name:
            raise InvalidCliRequest(
                _('Software profile name must be specified'))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        for node in api.getNodeList(software_profile_name):
            print(str(node))


def main():
    GetSoftwareProfileNodesCli().run()
