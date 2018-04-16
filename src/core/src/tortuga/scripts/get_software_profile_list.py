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

import argparse
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.softwareProfileWsApi import SoftwareProfileWsApi
from tortuga.cli.utils import FilterTagsAction


class GetSoftwareProfileListCli(TortugaCli):
    def parseArgs(self, usage=None):
        self.addOption(
            '--tag',
            dest='tags',
            action=FilterTagsAction,
            help=_('Filter results by specified tag(s) (comma-separated)'),
        )

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Return list of software profiles configured in'
                         ' the system'))

        api = SoftwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        for sp in api.getSoftwareProfileList(tags=self.getArgs().tags):
            print('%s' % (sp))


def main():
    GetSoftwareProfileListCli().run()


if __name__ == '__main__':
    main()
