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
from tortuga.wsapi.syncWsApi import SyncWsApi


class ScheduleUpdateCli(TortugaCli):
    """
    Schedule cluster update command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption('reason',
                       help='Reason for update (optional)',
                       nargs='?')
#        self.addOption('opts',
#                       help='Json string with additional options (optional)',
#                       nargs='?')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        api = self.configureClient(SyncWsApi)
        api.scheduleClusterUpdate(updateReason=self.getArgs().reason)
#        api.scheduleClusterUpdate(updateReason=self.getArgs().reason, opts=self.getArgs().opts if self.getArgs().opts else {})


def main():
    ScheduleUpdateCli().run()
