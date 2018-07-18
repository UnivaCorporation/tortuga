import argparse
from logging import getLogger
from typing import List, Optional


logger = getLogger(__name__)


class Command:
    """
    A CLI command.

    """
    sub_commands: List['Command'] = []
    arguments: List['Argument'] = []

    def __init__(self, *args, help: Optional[str] = None, **kwargs):
        """
        A command. args and kwargs are passed directly to
        subparsers.add_parser().

        :param args:
        :param kwargs:

        """
        self.args: list = args
        self.help: Optional[str] = help
        self.kwargs: dict = kwargs
        self.parent: 'Command' = None
        self.parser: Optional[argparse.ArgumentParser] = None

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

                help_ = command.get_help()
                if help_:
                    kwargs['help'] = help_

                kwargs.update(command.kwargs)

                suparser = subparsers.add_parser(*command.args, **kwargs)
                command.build_parser(suparser)

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
        Executes the command.

        :param argparse.Namespace args: the command arguments

        """
        pass


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


class Cli(Command):
    def __init__(self):
        super().__init__()

        #
        # Initialize the base parser and build it
        #
        parser_: argparse.ArgumentParser = argparse.ArgumentParser()
        self.build_parser(parser_)

    def run(self):
        """
        Runs the tortuga CLI utility.

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
