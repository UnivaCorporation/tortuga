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

# pylint: disable=no-member,maybe-no-member

import argparse
import gettext
import logging
import os
import sys
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.logging import CLI_NAMESPACE, ROOT_NAMESPACE
from tortuga.scripts.tortuga.script import ConfigException, \
    TortugaScriptConfig


T = TypeVar('T')


def check_for_root(cls):
    if os.getuid() != 0:
        sys.stderr.write('Command must be run as \'root\' user.\n')
        sys.stderr.flush()
        sys.exit(1)
    return cls


class TortugaCli(metaclass=ABCMeta):
    """
    Base tortuga command line interface class.
    """

    def __init__(self, validArgCount=0):
        self._logger = logging.getLogger(CLI_NAMESPACE)

        self._config: TortugaScriptConfig = None
        self._parser = argparse.ArgumentParser()
        self._args = []
        self._validArgCount = validArgCount
        self._optionGroupDict = {}
        self._cm = ConfigManager()

        self.__initializeLocale()

    def __initializeLocale(self):
        """Initialize the gettext domain """
        langdomain = 'tortugaStrings'

        # Locate the Internationalization stuff
        localedir = '../share/locale' \
            if os.path.exists('../share/locale') else \
            os.path.join(self._cm.getRoot(), 'share/locale')

        gettext.install(langdomain, localedir)

    def getParser(self):
        """ Get parser for this class. """
        return self._parser

    def addOption(self, *args, **kwargs):
        """ Add option. """
        self._parser.add_argument(*args, **kwargs)

    def addOptionToGroup(self, groupName, *args, **kwargs):
        """
        Add option for the given group name.
        Group should be created using addOptionGroup().
        """
        group = self._optionGroupDict.get(groupName)
        group.add_argument(*args, **kwargs)

    def addOptionGroup(self, groupName, desc):
        """ Add option group. """
        group = self._parser.add_argument_group(groupName, desc)
        self._optionGroupDict[groupName] = group
        return group

    def parseArgs(self, usage=None):
        """
        Parse args

        Raises:
            InvalidArgument
        """
        common_group = 'Common Tortuga Options'
        self.addOptionGroup(common_group, None)

        self.addOptionToGroup(common_group, '-V', action='store_true',
                              dest='cmdVersion', default=False,
                              help='print version and exit')

        self.addOptionToGroup(common_group, '-d', '--debug',
                              dest='consoleLogLevel', default='warning',
                              help='set debug level; valid values are: '
                                   'critical, error, warning, info, debug')

        self.addOptionToGroup(common_group, '--config', dest='config',
                              help='Path to config file '
                                   '(defaults to ~/.tortuga/config)')

        self.addOptionToGroup(common_group, '--url',
                              help='Tortuga web service URL')

        self.addOptionToGroup(common_group, '--username', dest='username',
                              help='Tortuga web service user name')

        self.addOptionToGroup(common_group, '--password', dest='password',
                              help='Tortuga web service password')

        self.addOptionToGroup(common_group, '--token', dest='token',
                              help='Tortuga web service token')

        self.addOptionToGroup(common_group, '--no-verify', dest='verify',
                              action='store_false', default=True,
                              help="Don't verify the API SSL certificate")

        if usage:
            self._parser.description = usage

        try:
            self._args = self._parser.parse_args()
        except SystemExit as rc:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(int(str(rc)))

        if self._args.cmdVersion:
            print('{0} version: {1}'.format(
                os.path.basename(sys.argv[0]),
                self._cm.getTortugaRelease()))
            sys.exit(0)

        self._setup_logging(self._args.consoleLogLevel)

        self._load_config(self._args)

        return self._args

    def _setup_logging(self, log_level_name: str):
        """
        Setup logging for the specified log level.

        :param str log_level_name: the name of the log level to use

        """
        log_level_name = log_level_name.upper()
        if log_level_name not in ['CRITICAL','ERROR', 'WARNING', 'INFO',
                                  'DEBUG']:
            print('Invalid debug level: {}'.format(log_level_name))
            sys.exit(0)

        log_level = getattr(logging, log_level_name)

        logger = logging.getLogger(ROOT_NAMESPACE)
        logger.setLevel(log_level)

        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

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

    def usage(self, s=None):
        """
        Print usage information
        """

        if s:
            sys.stderr.write('Error: {0}'.format(s)) + '\n'

        self._parser.print_help()

        sys.exit(1)

    def getArgs(self):
        return self._args

    def configureClient(self, client_class: Generic[T]) -> T:
        auth_method = self._config.get_auth_method()

        if auth_method == 'token':
            return client_class(token=self._config.token,
                                baseurl=self._config.url,
                                verify=self._config.verify)

        elif auth_method == 'password':
            return client_class(username=self._config.username,
                                password=self._config.password,
                                baseurl=self._config.url,
                                verify=self._config.verify)

        raise Exception('Unsupported auth method: {}'.format(auth_method))

    @abstractmethod
    def runCommand(self): \
            # pylint: disable=no-self-use
        """
        This method must be implemented by the derived class.
        """

    def run(self):
        """
        Invoke runCommand() in derivative class and handle exceptions.
        """
        try:
            self.runCommand()
        except TortugaException as ex:
            print(ex.getErrorMessage())
            raise SystemExit(ex.getErrorCode())
        except SystemExit:
            raise
        except Exception as ex:
            print(str(ex))
            raise SystemExit(-1)

    def _parseDiskSize(self, diskSizeParam): \
            # pylint: disable=no-self-use
        """
        Parses diskSizeParam, returns an int value representing
        number of megabytes

        Raises:
            ValueError
        """
        if diskSizeParam.endswith('TB'):
            return int(float(diskSizeParam[:-2]) * 1000000)

        if diskSizeParam.endswith('GB'):
            return int(float(diskSizeParam[:-2]) * 1000)
        elif diskSizeParam.endswith('MB'):
            # Must be an integer
            return int(diskSizeParam[:-2])

        return int(diskSizeParam)

    def _getDiskSizeDisplayStr(self, volSize): \
            # pylint: disable=no-self-use
        if volSize < 1000:
            result = '%s MB' % (volSize)
        elif volSize < 1000000:
            result = '%.3f GB' % (float(volSize) / 1000)
        else:
            result = '%.3f TB' % (float(volSize) / 1000000)

        return result
