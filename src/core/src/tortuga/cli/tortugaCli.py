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
import configparser
import gettext
import logging
import os
import sys
from abc import ABCMeta, abstractmethod

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.userNotAuthorized import UserNotAuthorized
from tortuga.utility.authManager import authorizeRoot


def check_for_root(cls):
    try:
        authorizeRoot()
    except UserNotAuthorized as exc:
        sys.stderr.write(str(exc) + '\n')
        sys.stderr.flush()
        sys.exit(1)

    return cls


class TortugaCli(metaclass=ABCMeta):
    """
    Base tortuga command line interface class.
    """

    def __init__(self, validArgCount=0):
        self._logger = logging.getLogger(
            'tortuga.cli.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

        self._parser = argparse.ArgumentParser()
        self._args = []
        self._validArgCount = validArgCount
        self._url = None
        self._username = None
        self._password = None
        self._optionGroupDict = {}
        self._cm = ConfigManager()

        self.__initializeLocale()

    def getLogger(self):
        """ Get logger for this class. """
        return self._logger

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
        commonGroup = _('Common Tortuga Options')
        self.addOptionGroup(commonGroup, None)

        self.addOptionToGroup(commonGroup, '-V', action='store_true',
                              dest='cmdVersion', default=False,
                              help=_('print version and exit'))

        self.addOptionToGroup(
            commonGroup, '-d', '--debug', dest='consoleLogLevel',
            help=_('set debug level; valid values are: critical, error,'
                   ' warning, info, debug'))

        self.addOptionToGroup(
            commonGroup, '--url',
            help=_('Tortuga web service URL'))

        self.addOptionToGroup(
            commonGroup, '--username', dest='username',
            help=_('Tortuga web service user name'))

        self.addOptionToGroup(
            commonGroup, '--password', dest='password',
            help=_('Tortuga web service password'))

        if usage:
            self._parser.description = usage

        try:
            self._args = self._parser.parse_args()
        except SystemExit as rc:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(int(str(rc)))

        if self._args.cmdVersion:
            print(_('{0} version: {1}'.format(
                os.path.basename(sys.argv[0]),
                self._cm.getTortugaRelease())))

            sys.exit(0)

        # Log level.
        consoleLogLevel = self._args.consoleLogLevel
        if consoleLogLevel:
            # logManager.setConsoleLogLevel(consoleLogLevel)

            logger = logging.getLogger('tortuga')

            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            logger.addHandler(ch)

        # Promote options to attributes
        url, username, password = self.__get_web_service_options()

        self._url = url
        self._username = username
        self._password = password

        return self._args

    def __get_web_service_options(self):
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

        # TORTUGA_WS_URL
        if self._args.url:
            # Command-line "--server" argument overrides env var and
            # setting contained within '/etc/profile.nii'
            url = self._args.url
        elif os.getenv('TORTUGA_WS_URL'):
            url = os.getenv('TORTUGA_WS_URL')

        # TORTUGA_WS_USERNAME
        if self._args.username:
            username = self._args.username
        elif os.getenv('TORTUGA_WS_USERNAME'):
            username = os.getenv('TORTUGA_WS_USERNAME')

        # TORTUGA_WS_PASSWORD
        if self._args.password:
            password = self._args.password
        elif os.getenv('TORTUGA_WS_PASSWORD'):
            password = os.getenv('TORTUGA_WS_PASSWORD')

        return url, username, password

    def usage(self, s=None):
        """
        Print usage information
        """

        if s:
            sys.stderr.write(_('Error: {0}').format(s) + '\n')

        self._parser.print_help()

        sys.exit(1)

    def getArgs(self):
        '''Returns the command line argument list'''
        return self._args

    def getUrl(self):
        return self._url

    def getUsername(self):
        """ Get user name. """
        return self._username

    def getPassword(self):
        """ Get password. """
        return self._password

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
            print('%s' % (ex.getErrorMessage()))
            raise SystemExit(ex.getErrorCode())
        except SystemExit as ex:
            raise
        except Exception as ex:
            print('%s' % (ex))
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
