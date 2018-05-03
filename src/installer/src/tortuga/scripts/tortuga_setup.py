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

import os
import sys
import logging
import logging.handlers
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.deployer import tortugaDeployer
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.exceptions.tortugaException import TortugaException


class TortugaSetup(TortugaCli):
    """
    Tortuga setup command-line interface.
    """

    def __init__(self):
        super(TortugaSetup, self).__init__()

        # Log all 'tortuga' APIs called during installation
        logger = logging.getLogger('tortuga')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.handlers.TimedRotatingFileHandler(
            '/var/log/tortuga_setup.log', when='midnight')
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        self._logger = logging.getLogger('tortuga.setup')
        self._logger.setLevel(logging.DEBUG)

        self.addOption(
            '--force', dest='force', action='store_true',
            default=False,
            help=_('Ignore installation safeguards and force installation'))

        self.addOption(
            '--defaults', dest='defaults', action='store_true',
            default=False,
            help=_('Use (sane) default settings'))

        self.addOption(
            '-i', dest='responseFile',
            help=_('Filename of Tortuga configuration file'))

        self.addOption(
            '--i-accept-the-eula', dest='acceptEula',
            action="store_true", default=False,
            help=_('Accept the Tortuga EULA.'))

        self.addOption(
            '--skip-kits', dest='skip_kits',
            help=_('Comma-separated list of kits ignore during installation'),
        )

    def runCommand(self):
        self._logger.info('=' * 75)
        self._logger.info('Installation started')
        self._logger.info('=' * 75)

        self.parseArgs(_("""
tortuga-setup is run after the installation of the Tortuga software
in order to configure the base cluster environment.
"""))

        self._logger.info('command-line args: %s' % (' '.join(sys.argv[1:])))

        if self.getArgs().responseFile:
            if not os.path.exists(self.getArgs().responseFile):
                raise InvalidCliRequest(
                    'Response file [%s] does not exist' % (
                        self.getArgs().responseFile))

        tortuga_cfg = {}

        if self.getArgs().responseFile:
            tortuga_cfg['inifile'] = self.getArgs().responseFile

        tortuga_cfg['acceptEula'] = self.getArgs().acceptEula
        tortuga_cfg['force'] = self.getArgs().force
        tortuga_cfg['defaults'] = self.getArgs().defaults
        tortuga_cfg['consoleLogLevel'] = self.getArgs().consoleLogLevel

        if self.getArgs().skip_kits:
            tortuga_cfg['skip_kits'] = self.getArgs().skip_kits

        try:
            tortugaDeployer.TortugaDeployer(
                self._logger, cmdline_options=tortuga_cfg).runSetup()

            self._logger.info('=' * 75)
            self._logger.info('Installation completed successfully')
            self._logger.info('=' * 75)
        except TortugaException:
            self._logger.info('=' * 75)
            self._logger.info('Installation failed')
            self._logger.info('=' * 75)

            raise


def main():
    TortugaSetup().run()
