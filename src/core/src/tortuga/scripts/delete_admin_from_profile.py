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
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest


class DeleteAdminFromProfileCli(TortugaCli):
    """
    Delete an admin from, a hw/sw profile command line interface.
    """

    def __init__(self):
        super().__init__()

    def parseArgs(self, usage=None):
        profile_attr_group = _('Profile Attribute Options')
        grp = self.addOptionGroup(
            profile_attr_group,
            _('Hardware or software profile must be specified.'))

        excl_group = grp.add_mutually_exclusive_group(required=True)

        excl_group.add_argument(profile_attr_group,
                                '--software-profile', dest='swprofile',
                                help=_('hardware profile name'))
        excl_group.add_argument(profile_attr_group, '--hardware-profile',
                                dest='hwprofile',
                                help=_('software profile name'))

        profile_attr_group = _('Admin Attribute Options')
        self.addOptionGroup(
            profile_attr_group, _('Admin username must be specified.'))
        self.addOptionToGroup(profile_attr_group, required=True,
                              '--admin-username', dest='adminUsername',
                              help=_('Admin username'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Removes association between an existing adminstrative user and hardware or
software profile.
"""))

        swprofile = self.getArgs().swprofile
        hwprofile = self.getArgs().hwprofile

        admin_username = self.getArgs().adminUsername

        if swprofile:
            profile = swprofile

            api = SoftwareProfileWsApi(username=self.getUsername(),
                                       password=self.getPassword(),
                                       baseurl=self.getUrl())
        else:
            profile = hwprofile

            api = HardwareProfileWsApi(username=self.getUsername(),
                                       password=self.getPassword(),
                                       baseurl=self.getUrl())

        api.deleteAdmin(profile, admin_username)


def main():
    DeleteAdminFromProfileCli().run()
