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
from tortuga.exceptions import softwareProfileNotFound
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi


class DeleteSoftwareProfileCli(TortugaCli):
    def __init__(self):
        super().__init__()
        option_group_name = _('Delete Software Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--name',
                              dest='softwareProfileName',
                              help=_('Name of software profile to delete'))

    def runCommand(self):
        self.parseArgs(_("""
    delete-software-profile --name=NAME

Description:
    The delete-software-profile tool removes a software profile  from  the
    system.   There  can not be any nodes currently assigned to the soft-
    ware profile for it be successfully removed.
"""))

        if not self.getArgs().softwareProfileName:
            raise InvalidCliRequest(
                _('Software profile name must be specified'))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())
        try:
            api.deleteSoftwareProfile(
                self.getArgs().softwareProfileName)
        except softwareProfileNotFound.SoftwareProfileNotFound:
            print(_('Software profile [%s] not found' % (
                self.getArgs().softwareProfileName)))


def main():
    DeleteSoftwareProfileCli().run()
