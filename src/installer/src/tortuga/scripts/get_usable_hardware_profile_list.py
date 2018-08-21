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
from tortuga.db.dbManager import DbManager
from tortuga.db.softwareUsesHardwareDbApi import SoftwareUsesHardwareDbApi
from tortuga.hardwareprofile.hardwareProfileApi import HardwareProfileApi
from tortuga.kit.loader import load_kits
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi


class GetUsableHardwareProfileListCli(TortugaCli):
    """
    Get software uses hardware command line interface.
    """

    def runCommand(self):
        self.parseArgs(_("""
Lists all software to hardware profile mappings in the system.
"""))
        load_kits()

        softwareUsesHardwareDbApi = SoftwareUsesHardwareDbApi()

        hwApi = HardwareProfileApi()
        swApi = SoftwareProfileApi()

        with DbManager().session() as session:
            hwPList = hwApi.getHardwareProfileList(session)
            swPList = swApi.getSoftwareProfileList(session)

            mappingList = softwareUsesHardwareDbApi.getSoftwareUsesHardwareList(session)

        print('Current mappings:')
        print('Software Profile               Hardware Profile')
        for mapping in mappingList:
            outputString = ''
            for sp in swPList:
                if sp.getId() == mapping[0]:
                    outputString += ' %s' % sp.getName()
                    outputString = outputString.ljust(32)
            for hp in hwPList:
                if hp.getId() == mapping[1]:
                    outputString += '%s' % hp.getName()

            print(outputString)


def main():
    GetUsableHardwareProfileListCli().run()
