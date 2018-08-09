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

import errno
import signal

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.dbManager import DbManager
from tortuga.kit.actions.manager import KitActionsManager
from tortuga.kit.loader import load_kits
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi


class PreAddHostCli(TortugaCli):
    """
    pre-add-host cli
    """

    def parseArgs(self, usage=None):
        self.addOption('--hardware-profile', dest='hardwareProfile',
                       help=_('Hardware profile nodes were added to.'))

        self.addOption("--software-profile", dest='softwareProfile',
                       metavar='NAME',
                       help=_('Software profile nodes were added to.'))

        self.addOption('--host-name', dest='hostname',
                       help=_('Host name of node being added.'))

        self.addOption('--ip', dest='ip',
                       help=_('IP address of node being added.'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        load_kits()

        with DbManager().session() as session:
            if self.getArgs().softwareProfile:
                # Check for valid software profile - will throw exception and exit
                # if it doesn't exist

                SoftwareProfileApi().getSoftwareProfile(
                    session, self.getArgs().softwareProfile)

            # Restore default signal masks/handlers so subprocesses don't inherit
            # unexpected signal masks
            # IMPORTANT NOTE:
            # Python does not appear to allow you to clear the ignore mask for
            # SIGPIPE. All subprocesses
            # created through this method will still ignore SIGPIPE unless they
            # explicitly do otherwise themselves after startup. This could
            # potentially cause issues with some system daemons in the future if
            # one of them uses SIGPIPE.

            for signum in range(1, signal.NSIG):
                try:
                    signal.signal(signum, signal.SIG_DFL)
                except OSError as exc:
                    # Signal numbers are not necessarily contiguous;
                    # ignore non-existent signals
                    if exc.errno == errno.EINVAL:
                        continue

                    raise

            kitmgr = KitActionsManager()
            kitmgr.session = session

            kitmgr.pre_add_host(
                self.getArgs().hardwareProfile,
                self.getArgs().softwareProfile,
                self.getArgs().hostname,
                self.getArgs().ip)


def main():
    PreAddHostCli().run()
