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

import logging

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.kit.builder import KitBuilder
from tortuga.kit.builder import logger as kit_builder_logger


class BuildKit(TortugaCli):
    def __init__(self):
        super().__init__(validArgCount=1)
        #
        # Output build log messages to the console by default
        #
        kit_builder_logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(name)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        kit_builder_logger.addHandler(console_handler)

    def parseArgs(self, usage=None):

        parser = self.getParser()

        parser.set_defaults(subcommand='build')

        subparsers = parser.add_subparsers(title='subcommands',
                                           description='valid subcommands',
                                           help='additional help')

        build_subparser = subparsers.add_parser('build')
        build_subparser.set_defaults(subcommand='build')
        clean_subparser = subparsers.add_parser('clean')
        clean_subparser.set_defaults(subcommand='clean')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        #
        # Initialize the kit builder
        #
        _kit_builder = KitBuilder()

        command = self.getArgs().subcommand
        if command == 'build':
            _kit_builder.build()
        elif command == 'clean':
            _kit_builder.clean()


def main():
    BuildKit().run()
