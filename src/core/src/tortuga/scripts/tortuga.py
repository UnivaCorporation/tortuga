import argparse
import configparser
import logging
import os
import sys
from typing import Dict, List

import yaml

from tortuga.config.configManager import ConfigManager
from tortuga.wsapi_v2.client import TortugaWsApiClient


logger = logging.getLogger(__name__)


class Tortuga:
    def __init__(self):
        logger.addHandler(logging.NullHandler())

        self._parser: argparse.ArgumentParser = argparse.ArgumentParser()
        self._args: object = None
        self._url: str = None
        self._username: str = None
        self._password: str = None
        self._cm: ConfigManager = ConfigManager()

    def initialize_options(self):
        self._parser.add_argument(
            'cmd',
            type=str,
            nargs='*',
            help='Command, action, and arguments (i.e. events list)'
        )

        self._parser.add_argument(
            '-q', '--query',
            type=str,
            nargs='*',
            help='Query parameters for command, if applicable'
        )

        self._parser.add_argument(
            '-v', '--version',
            action='store_true',
            dest='version',
            default=False,
            help='print version and exit'
        )

        self._parser.add_argument(
            '-d', '--debug',
            dest='debug',
            help='set debug level; valid values are: critical, error, '
                 'warning, info, debug'
        )

        self._parser.add_argument(
            '--url',
            help='Tortuga web service URL'
        )

        self._parser.add_argument(
            '--username',
            dest='username',
            help='Tortuga web service user name'
        )

        self._parser.add_argument(
            '--password',
            dest='password',
            help='Tortuga web service password'
        )

    def parse_args(self):
        try:
            self._args = self._parser.parse_args()
        except SystemExit as rc:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(int(str(rc)))

        self._version()
        self._set_log_level()
        self._set_web_service_params()

        return self._args

    def _version(self):
        if self._args.version:
            print(
                '{0} version: {1}'.format(
                    os.path.basename(sys.argv[0]),
                    self._cm.getTortugaRelease()
                )
            )
            sys.exit(0)

    def _set_log_level(self):
        if self._args.debug:
            root_logger = logging.getLogger('tortuga')
            root_logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            root_logger.addHandler(ch)

    def _set_web_service_params(self):
        url, username, password = self._get_web_service_options()
        self._url = url
        self._username = username
        self._password = password

    def _get_web_service_options(self):
        """
        Read Tortuga web service credentials from config file, environment,
        or command-line. Command-line overrides either config file or
        environment.

        :return: tuple of (url, username, password)

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

        if self._args.url:
            url = self._args.url
        elif os.getenv('TORTUGA_WS_URL'):
            url = os.getenv('TORTUGA_WS_URL')

        if self._args.username:
            username = self._args.username
        elif os.getenv('TORTUGA_WS_USERNAME'):
            username = os.getenv('TORTUGA_WS_USERNAME')

        if self._args.password:
            password = self._args.password
        elif os.getenv('TORTUGA_WS_PASSWORD'):
            password = os.getenv('TORTUGA_WS_PASSWORD')

        return url, username, password

    def run(self):
        try:
            self._run()
        except Exception as ex:
            print(ex)
            raise SystemExit(-1)
        except SystemExit:
            raise

    def _run(self):
        self.initialize_options()
        args = self.parse_args()

        cmd = args.cmd
        if cmd:
            self._run_cmd(cmd, args.query)

    def _run_cmd(self, cmd: List[str], query: List[str]):
        if not cmd:
            cmd = []

        if not query:
            query = []

        if len(cmd) == 1:
            print('Command action is required')
            raise SystemExit(-1)

        ws = TortugaWsApiClient(endpoint=cmd[0])
        params = self._parse_params(query)
        if cmd[1] == 'list':
            self._pretty_print(ws.list(**params))
        if cmd[1] == 'show':
            self._pretty_print(ws.get(cmd[2]))

    def _pretty_print(self, data):
        print(yaml.safe_dump(data, default_flow_style=False))

    def _parse_params(self, query: List[str]) -> Dict[str, str]:
        params = {}
        for q in query:
            parts = q.split('=')
            params[parts[0]] = parts[1]
        return params


def main():
    Tortuga().run()
