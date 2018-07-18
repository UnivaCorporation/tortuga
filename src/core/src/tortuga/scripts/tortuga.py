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
import configparser
import json
import logging
import os
import sys
from typing import List, Optional

from tortuga.cli.base import Argument, Cli, Command
from tortuga.cli.commands.listen import ListenCommand
from tortuga.cli.commands.tortuga_ws import TortugaWsCommand
from tortuga.cli.commands.unisight_ws import RulesCommand
from tortuga.config.configManager import ConfigManager


logger = logging.getLogger(__name__)


class TortugaNew(Cli):
    CONFIG_FILE = 'tortuga_cli.json'

    sub_commands = [
        ListenCommand(
            'listen',
            help='Listen on the API websocket for events'
        ),
        TortugaWsCommand(
            'events',
            help='Events API'
        )
    ]

    arguments = [
        Argument(
            '-v', '--version',
            action='store_true',
            dest='version',
            default=False,
            help='print version and exit'
        ),
        Argument(
            '-d', '--debug',
            dest='debug',
            help='set debug level; valid values are: critical, error, '
                 'warning, info, debug'
        ),
        Argument(
            '--url',
            help='Tortuga web service URL'
        ),
        Argument(
            '--username',
            dest='username',
            help='Tortuga web service user name'
        ),
        Argument(
            '--password',
            dest='password',
            help='Tortuga web service password'
        )
    ]

    def __init__(self):
        self.config_manager: ConfigManager = ConfigManager()
        self.config: dict = self._load_config()
        self.url: str = None
        self.username: str = None
        self.password: str = None
        super().__init__()

    def _load_config(self) -> dict:
        """
        Loads the config from the config file, if found, otherwise
        and empty config is returned. The config file is a JSON file
        with the following (optional) settings:

        {
            "unisight": {
                "api": "https://unisight.example.com:1234,
                "username": "api_username",
                "password": "api_password"
            }
        }

        :return dict: the config dict

        """
        config_file_path = os.path.join(
            self.config_manager.getRoot(),
            'config',
            self.CONFIG_FILE
        )

        if not os.path.exists(config_file_path):
            return {}

        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)

        return config

    def pre_execute(self, args: argparse.Namespace):
        self._version(args)
        self._set_log_level(args)
        self._set_web_service_vars(args)

    def _version(self, args: argparse.Namespace):
        """
        Implements the --version argument.

        """
        if args.version:
            print(
                '{0} version: {1}'.format(
                    os.path.basename(sys.argv[0]),
                    self.config_manager.getTortugaRelease()
                )
            )
            sys.exit(0)

    def _set_log_level(self, args: argparse.Namespace):
        """
        Implements the --debug argument.

        """
        if args.debug:
            root_logger = logging.getLogger('tortuga')
            root_logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            root_logger.addHandler(ch)

    def _set_web_service_vars(self, args: argparse.Namespace):
        """
        Read Tortuga web service credentials from config file, environment,
        or command-line. Command-line overrides either config file or
        environment.

        """
        username = password = url = None

        cfg_file = os.path.join(os.path.expanduser('~'),
                                '.local',
                                'tortuga',
                                'credentials')

        if os.path.exists(cfg_file):
            cfg = configparser.ConfigParser()

            cfg.read(cfg_file)

            username = cfg.get('default', 'username') \
                if cfg.has_section('default') and \
                cfg.has_option('default', 'username') else None

            password = cfg.get('default', 'password') \
                if cfg.has_section('default') and \
                cfg.has_option('default', 'password') else None

            url = cfg.get('default', 'url') \
                if cfg.has_section('default') and \
                cfg.has_option('default', 'url') else None

        if args.url:
            url = args.url
        elif os.getenv('TORTUGA_WS_URL'):
            url = os.getenv('TORTUGA_WS_URL')

        if args.username:
            username = args.username
        elif os.getenv('TORTUGA_WS_USERNAME'):
            username = os.getenv('TORTUGA_WS_USERNAME')

        if args.password:
            password = args.password
        elif os.getenv('TORTUGA_WS_PASSWORD'):
            password = os.getenv('TORTUGA_WS_PASSWORD')

        if username is None and password is None:
            logger.debug('Using built-in user credentials')
            username = self.config_manager.getCfmUser()
            password = self.config_manager.getCfmPassword()

        self.url = url
        self.username = username
        self.password = password

    def get_sub_commands(self) -> List[Command]:
        sub_commands = super().get_sub_commands()

        rules_command = self._get_rules_command()
        if rules_command:
            sub_commands.append(rules_command)

        return sub_commands

    def _get_rules_command(self) -> Optional[Command]:
        """
        If a Unisight API is configured, get the Rules Command instance for
        that configuration.

        :return Optional[Command]: the Unisight Command instance, if
                                   configured, otherwise None

        """
        unisight_config = self.config.get('unisight', None)
        if not unisight_config:
            return None

        return RulesCommand(
            'rules',
            config=unisight_config,
            help='Unisight rules API'
        )


def main():
    """
    Main.

    """
    TortugaNew().run()
