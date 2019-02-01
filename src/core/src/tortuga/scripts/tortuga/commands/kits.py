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

from tortuga.cli.base import Argument, Command, RootCommand
from tortuga.kit.builder import KitBuilder


class BuildCommand(Command):
    """
    Builds a kit.

    """
    arguments = [
        Argument(
            '-v', '--version',
            dest='kit_version',
            default=None,
            help='Override the x.y.z version in kit.json'
        ),
        Argument(
            '-i', '--ignore-directory-version',
            dest='ignore_directory_version',
            action='store_true',
            default=False,
            help='Do not rename package to tortuga_kits/<name>_<version>'
        )
    ]
    name = 'build'
    help = 'Builds the kit in the current directory'

    def execute(self, args: argparse.Namespace):
        builder = KitBuilder(
            version=args.kit_version,
            ignore_directory_version=args.ignore_directory_version
        )
        builder.build()


class CleanCommand(Command):
    """
    Cleans a kit build directory.

    """
    name = 'clean'
    help = 'Cleans the kit build in the current directory'

    def execute(self, args: argparse.Namespace):
        builder = KitBuilder()
        builder.clean()


class KitsCommand(RootCommand):
    """
    Listen command for listening to websocket events.

    """
    name = 'kits'
    help = 'Kits management'

    sub_commands = [
        BuildCommand(),
        CleanCommand()
    ]
