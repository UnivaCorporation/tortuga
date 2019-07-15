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
import json
import logging
import os
import sys
from typing import Optional

from marshmallow import fields, Schema, ValidationError

from tortuga.cli.base import Argument, Cli, Config, ConfigException
from tortuga.config.configManager import ConfigManager
from tortuga.logging import CLI_NAMESPACE, ROOT_NAMESPACE
from tortuga.os_utility.tortugaSubprocess import executeCommand


logger = logging.getLogger(CLI_NAMESPACE)


class TortugaScriptConfigSchema(Schema):
    navops_cli = fields.String()
    url = fields.String()
    username = fields.String()
    password = fields.String()
    token = fields.String()


class ConfigFileNotFoundException(ConfigException):
    pass


class TortugaScriptConfig(Config):
    NAVOPS_CLI = '/opt/navops-launch/bin/navopsctl'
    DEFAULT_FILENAME = os.path.join(os.path.expanduser('~'),
                                    '.tortuga', 'config')

    def __init__(self, **kwargs):
        #
        # Internal properties
        #
        self._filename = None
        self._cm = ConfigManager()

        #
        # Determine the username/password to use as default
        #
        default_username = self._cm.getCfmUser()
        default_password = self._cm.getCfmPassword()
        if default_password == 'not-set':
            default_username = None
            default_password = None

        #
        # Check for default navops cli location
        #
        default_navops_cli = self.NAVOPS_CLI
        if not os.path.exists(default_navops_cli):
            default_navops_cli = None

        #
        # Configuration settings
        #
        self.url = kwargs.get('url', self._cm.getInstallerUrl())
        self.token = kwargs.get('token', None)
        self.navops_cli = kwargs.get('navops_cli', default_navops_cli)
        self.username = kwargs.get('username', default_username)
        self.password = kwargs.get('password', default_password)
        self.verify = True

    def _load_from_environment(self):
        if os.getenv('TORTUGA_WS_URL'):
            self.url = os.getenv('TORTUGA_WS_URL')
        if os.getenv('TORTUGA_WS_USERNAME'):
            self.username = os.getenv('TORTUGA_WS_USERNAME')
        if os.getenv('TORTUGA_WS_PASSWORD'):
            self.password = os.getenv('TORTUGA_WS_PASSWORD')
        if os.getenv('TORTUGA_WS_TOKEN'):
            self.token = os.getenv('TORTUGA_WS_TOKEN')
        if os.getenv('TORTUGA_WS_NO_VERIFY'):
            self.verify = False

    @classmethod
    def load(cls, filename: str = None) -> 'TortugaScriptConfig':
        #
        # If a file name is provided, then we try to load that first
        #
        if filename:
            config = cls._load_from_file(filename)
        #
        # If no filename is provided, then we have to figure out where to
        # get a configuration
        #
        else:
            #
            # First, check if the user has a config in their home directory
            #
            if os.path.exists(cls.DEFAULT_FILENAME):
                config = cls._load_from_file(cls.DEFAULT_FILENAME)
            #
            # Otherwise, create a new config from scratch
            #
            else:
                config = cls()
        #
        # Override the config with any settings provided from the
        # environment
        #
        config._load_from_environment()

        return config

    @classmethod
    def _load_from_file(cls, filename) -> 'TortugaScriptConfig':
        if not os.path.exists(filename):
            raise ConfigFileNotFoundException(
                'Config file not found: {}'.format(filename)
            )

        with open(filename) as fp:
            try:
                config_data = json.load(fp)
            except json.JSONDecodeError:
                raise ConfigException(
                    'Invalid config file: {}'.format(filename))

        try:
            unmarshalled = TortugaScriptConfigSchema().load(config_data)
        except ValidationError:
            raise ConfigException('Invalid config file: {}'.format(filename))

        return TortugaScriptConfig(**unmarshalled.data)

    def save(self, filename: str = None):
        if not filename:
            if self._filename:
                filename = filename
            else:
                filename = TortugaScriptConfig.DEFAULT_FILENAME

        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True, mode=0o700)

        marshalled = TortugaScriptConfigSchema().dump(self)
        with open(filename, 'w') as fp:
            json.dump(marshalled.data, fp, indent=4)

    def get_auth_method(self) -> str:
        """
        Gets the authentication method that should be used.

        :return str: token or password

        :raises ConfigException: if no auth method is configured

        """
        if self.navops_cli or self.token:
            return 'token'

        if self.username and self.password:
            return 'password'

        raise ConfigException('Authentication required. Use "tortuga login".')

    def get_token(self) -> str:
        """
        Gets the current authentication token.

        :return str: the token

        :raises ConfigException: if token is unavailable

        """
        if self.navops_cli:
            return self._get_navops_token()

        if self.token:
            return self.token

        raise ConfigException('Authentication required. Use "tortuga login".')

    def _get_navops_token(self) -> str:
        cmd = '{} token'.format(self.navops_cli)
        p = executeCommand(cmd)

        if p.getExitStatus() != 0:
            raise ConfigException(p.getStdErr())

        return p.stdout


class TortugaScript(Cli):
    """
    The Tortuga Cli implementation.

    """
    command_package = 'tortuga.scripts.tortuga.commands'

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
            '--config',
            dest='config',
            help='Path to config file (defaults to ~/.tortuga/config)'
        ),
        Argument(
            '--url',
            help='Web service URL'
        ),
        Argument(
            '--username',
            dest='username',
            help='Web service user name'
        ),
        Argument(
            '--password',
            dest='password',
            help='Web service password'
        ),
        Argument(
            '--token',
            dest='token',
            help='Web service token'
        ),
        Argument(
            '--no-verify',
            dest='verify',
            default=True,
            action='store_false',
            help="Don't verify the API SSL certificate"
        ),
        Argument(
            '--json',
            dest='fmt',
            default='yaml',
            action='store_const',
            const='json',
            help='Output as JSON',
        )
    ]

    def __init__(self):
        super().__init__()
        self._config: Optional[TortugaScriptConfig] = None

    def get_command_package(self):
        return 'tortuga.cli.commands'

    def pre_execute(self, args: argparse.Namespace):
        self._version(args)
        self._set_log_level(args)
        self._load_config(args)

    def _version(self, args: argparse.Namespace):
        """
        Implements the --version argument.

        """
        if args.version:
            cm = ConfigManager()

            print(
                '{0} version: {1}'.format(
                    os.path.basename(sys.argv[0]),
                    cm.getTortugaRelease()
                )
            )
            sys.exit(0)

    def _set_log_level(self, args: argparse.Namespace):
        """
        Implements the --debug argument.

        """
        if args.debug:
            root_logger = logging.getLogger(ROOT_NAMESPACE)
            root_logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            root_logger.addHandler(ch)

    def _load_config(self, args: argparse.Namespace):
        """
        Implements the --config argument.

        """
        #
        # Load a config, filename may or may-not be provided...
        #
        try:
            self._config = TortugaScriptConfig.load(args.config)

        except ConfigException as ex:
            print(str(ex))
            sys.exit(0)

        #
        # Override the config with any provided argument values
        #
        if args.url:
            self._config.url = args.url
        if args.username:
            self._config.username = args.username
        if args.password:
            self._config.password = args.password
        if args.token:
            self._config.token = args.token
        self._config.verify = args.verify

    def get_config(self) -> Optional[TortugaScriptConfig]:
        return self._config


def main():
    """
    Main.

    """
    TortugaScript().run()
