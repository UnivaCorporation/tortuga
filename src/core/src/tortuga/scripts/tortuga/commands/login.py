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
from getpass import getpass
import sys

from tortuga.cli.base import RootCommand
from tortuga.os_utility.tortugaSubprocess import TortugaSubprocess
from ..script import TortugaScriptConfig


class LoginCommand(RootCommand):
    """
    Login to the CLI.

    """
    name = 'login'
    help = 'Login to the CLI'

    def execute(self, args: argparse.Namespace):
        """
        Logs the user in to the CLI.

        """
        config: TortugaScriptConfig = self.get_config()
        if config.navops_cli:
            self._login_navops(config)
        else:
            config.username = input('Username: ').strip()
            config.password = getpass()

        config.save()

    def _login_navops(self, config: TortugaScriptConfig):
        cmd = '{} login'.format(config.navops_cli)
        p = TortugaSubprocess(cmd, stdin=sys.stdin, stdout=sys.stdout,
                              stderr=sys.stderr)
        p.run()

        if p.getExitStatus() != 0:
            sys.exit(1)
