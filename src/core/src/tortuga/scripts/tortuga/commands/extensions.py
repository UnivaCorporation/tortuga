import argparse
import io
from logging import getLogger
import subprocess
from typing import List
from xml.etree.ElementTree import ElementTree

import requests

from tortuga.cli.base import RootCommand, Command, Argument
from tortuga.cli.utils import pretty_print
from tortuga.config.configManager import ConfigManager


logger = getLogger(__name__)


class ListCommand(Command):
    """
    List available extensions.

    """
    name = 'list'
    help = 'List available extensions'

    def execute(self, args: argparse.Namespace):
        pretty_print(get_available_extensions())


class InstallCommand(Command):
    """
    Install an extension.

    """
    name = 'install'
    help = 'Install an extension'

    arguments = [
        Argument(
            'name',
            help='The name of the extension'
        )
    ]

    def execute(self, args: argparse.Namespace):
        available_extensions = get_available_extensions()
        if args.name not in available_extensions:
            raise Exception(
                '{} is not a valid extension name'.format(args.name))

        cm = ConfigManager()

        pip_cmd = [
            'pip', 'install',
            '--extra-index-url', get_python_package_repo(),
            '--trusted-host', cm.getInstaller(),
            args.name
        ]

        subprocess.Popen(pip_cmd).wait()


class ExtensionsCommand(RootCommand):
    """
    Command for managing Tortuga CLI extensions.

    """
    name = 'extensions'
    help = 'Manage Tortuga CLI extensions'

    sub_commands = [
        ListCommand(),
        InstallCommand()
    ]


def get_python_package_repo() -> str:
    """
    Gets the URL to the Tortuga Python package repository.

    :return str: the URL

    """
    cm = ConfigManager()

    int_webroot = cm.getIntWebRootUrl(cm.getInstaller())

    return '{}/python-tortuga/simple/'.format(int_webroot)


def get_available_extensions() -> List[str]:
    r = requests.get(get_python_package_repo())
    if r.status_code != 200:
        raise Exception(
            'Repository returned status code: {}'.format(r.status_code)
        )

    tree = ElementTree()
    root = tree.parse(io.StringIO(r.text))

    extensions = []
    for e in root.findall('body/a'):
        name = e.text
        if 'cli' in name:
            extensions.append(name)

    return extensions
