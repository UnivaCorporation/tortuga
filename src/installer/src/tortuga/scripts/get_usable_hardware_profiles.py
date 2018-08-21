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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.dbManager import DbManager
from tortuga.db.softwareUsesHardwareDbApi import SoftwareUsesHardwareDbApi
from tortuga.hardwareprofile.hardwareProfileApi import HardwareProfileApi
from tortuga.kit.loader import load_kits


class GetUsableHardwareProfilesCli(TortugaCli):
    """
    Display hardware profiles mapped to specified software profile
    """

    def parseArgs(self, usage=None):
        self.addOption('--software-profile', dest='swprofile', metavar='NAME',
                       required=True,
                       help=_('software profile'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Show the software to hardware profile mappings for the specified software
profile."""))

        load_kits()

        softwareUsesHardwareDbApi = SoftwareUsesHardwareDbApi()

        with DbManager().session() as session:
            api = HardwareProfileApi()

            hardwareProfileIdList = softwareUsesHardwareDbApi.\
                getAllowedHardwareProfilesBySoftwareProfileName(
                    session, self.getArgs().swprofile)

            print('Software Profile [%s] is allowed to use the following'
                ' hardware profiles:' % (self.getArgs().swprofile))

            for hardwareProfileId in hardwareProfileIdList:
                for hp in api.getHardwareProfileList(session):
                    if hp.getId() == hardwareProfileId:
                        print(hp.getName())


def main():
    GetUsableHardwareProfilesCli().run()
