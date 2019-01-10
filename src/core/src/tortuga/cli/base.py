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
import importlib
import logging
import pkgutil
from typing import List, Optional, Type

from tortuga.logging import CLI_NAMESPACE


class Command:
    """
    A CLI command.

    """
    name = None
    help = None
    sub_commands: List['Command'] = []
    arguments: List['Argument'] = []

    def __init__(self):
        """
        A command.

        """
        self.parent: 'Command' = None
        self.parser: Optional[argparse.ArgumentParser] = None
        self._logger = logging.getLogger(CLI_NAMESPACE)

    def set_parent(self, parent: 'Command'):
        """
        Sets the parent command.

        :param Command parent: the parent command instance

        """
        self.parent = parent

    def build_parser(self, parser: argparse.ArgumentParser):
        """
        Builds up the passed-in parser with arguments and sub-parsers.

        :param Cli cli                       : the base Cli instance that
                                               this command belongs to
        :param argparse.ArgumentParser parser: the parser to build
        :param Command parent                : the parent command, if any

        """
        self.parser = parser

        #
        # Add arguments
        #
        for arg in self.get_arguments():
            arg.set_command(self)
            arg.build_argument(parser)

        #
        # Ensure the command instance is included when parsing arguments
        #
        parser.set_defaults(command=self)

        #
        # Add sub-commands
        #
        sub_commands = self.get_sub_commands()
        if sub_commands:
            subparsers = parser.add_subparsers()
            for command in sub_commands:
                command.set_parent(self)

                kwargs = {}
                if command.get_help():
                    kwargs['help'] = command.get_help()

                suparser = subparsers.add_parser(command.get_name(), **kwargs)
                command.build_parser(suparser)

    def get_name(self) -> str:
        """
        Gets the name for this command.

        :return str: the command name

        """
        return self.name

    def get_help(self) -> Optional[str]:
        """
        Gets the help string for this command.

        :return Optional[str]: the help string for this command

        """
        return self.help

    def get_sub_commands(self) -> List['Command']:
        """
        Gets the list of sub-commands for this command.

        :return List[Command]: the list of command instances

        """
        return self.sub_commands

    def get_arguments(self) -> List['Argument']:
        """
        Gets the list of arguments for this command.

        :return List[Argument]: the list of arguments

        """
        return self.arguments

    def execute(self, args: argparse.Namespace):
        """
        Executes the command.  If not overloaded,
        print parser help.

        :param argparse.Namespace args: the command arguments

        """
        self.parser.print_help()


class Argument:
    """
    A command argument.

    """
    def __init__(self, *args, help: Optional[str] = None, **kwargs):
        """
        A command argument. args and kwargs are passed directly to
        parser.add_argument().

        :param args:
        :param kwargs:

        """
        self.args: list = args
        self.help: Optional[str] = help
        self.kwargs: dict = kwargs
        self.command: Command = None
        self.parser: Optional[argparse.ArgumentParser] = None

    def set_command(self, command: Command):
        """
        Sets the parent command for this argument.

        :param Command command: the parent command to set

        """
        self.command = command

    def get_help(self) -> Optional[str]:
        """
        Gets the help text for this argument.

        :return Optional[str]: the help text for this command

        """
        return self.help

    def build_argument(self, parser: argparse.ArgumentParser):
        """
        Builds the argument in the given parser.

        :param argparse.ArgumentParser parser: the parser in which to build
                                               the argument

        """
        self.parser = parser

        kwargs = {}
        help_ = self.get_help()
        if help_:
            kwargs['help'] = help_

        kwargs.update(self.kwargs)

        parser.add_argument(*self.args, **kwargs)


class RootCommand(Command):
    """
    A root level command, used at the top level of the command hierarchy.
    This is the class that is searched for by the loader.

    """
    pass


class Cli(Command):
    command_package: str = None

    def __init__(self):
        super().__init__()

        #
        # Initialize the base parser and build it
        #
        parser_: argparse.ArgumentParser = argparse.ArgumentParser()
        self.build_parser(parser_)

    def run(self):
        """
        Runs CLI utility.

        """
        try:
            args = self.parser.parse_args()
            self.pre_execute(args)
            args.command.execute(args)
        except Exception as ex:
            print(ex)
            raise SystemExit(-1)
        except SystemExit:
            raise

    def pre_execute(self, args: argparse.Namespace):
        """
        Executed by run prior to the actual command getting executed.

        :param argparse.Namespace args: the parsed arguments

        """
        pass

    def get_command_package_name(self) -> str:
        """
        Returns the fully qualified Python package that will be searched
        for RootCommand subclasses.

        :return str: a fully qualified Python package name

        """
        if not self.command_package:
            raise Exception('CLI command package not defined')

        return self.command_package

    def get_sub_commands(self) -> List[Command]:
        commands = []

        for command_class in self._find_commands():
            commands.append(command_class())

        return commands

    def _find_commands(self) -> List[Type[RootCommand]]:
        """
        Finds all RootCommand classes by searching through all modules
        in the tortuga.cli.commands package.

        :return List[Type[RootCommand]]: a list of all RootCommand classes

        """
        subclasses = []

        def look_for_subclass(module_name):
            module = importlib.import_module(module_name)

            d = module.__dict__
            for key, entry in d.items():
                if key == RootCommand.__name__:
                    continue

                try:
                    if issubclass(entry, RootCommand):
                        subclasses.append(entry)

                except TypeError:
                    continue

        pkg_name = self.get_command_package_name()
        pkg = importlib.import_module(pkg_name)
        for _, modulename, _ in pkgutil.walk_packages(pkg.__path__):
            look_for_subclass('{}.{}'.format(pkg_name, modulename))

        return subclasses
