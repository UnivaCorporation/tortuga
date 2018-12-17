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

import os.path
import sys
import json
import configparser
import argparse
from typing import List, Dict, Optional

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.wsapi.resourceAdapterConfigurationWsApi \
    import ResourceAdapterConfigurationWsApi
from tortuga.wsapi.resourceAdapterWsApi import ResourceAdapterWsApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.resourceAdapterNotFound \
    import ResourceAdapterNotFound
from tortuga.exceptions.resourceNotFound import ResourceNotFound
from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists


class AdapterMgmtCLI(TortugaCli):
    def __init__(self):
        super().__init__()

        self.subparser_update = None
        self.api = None

    def parseArgs(self, usage=None):
        common_args = argparse.ArgumentParser(add_help=False)
        common_args.add_argument('--verbose', action='store_true',
                                 help='Enable verbose output')
        common_args.add_argument(
            '--resource-adapter', '-r', metavar='NAME', required=True,
            help='Resource adapter name')

        show_list_common_args = argparse.ArgumentParser(add_help=False)
        show_list_common_args.add_argument('--json', action='store_true',
                                           help='JSON output')

        create_update_common_args = argparse.ArgumentParser(add_help=False)
        create_update_common_args.add_argument(
            '--setting', '-s', metavar="KEY=VALUE",
            action='append', type=key_value_pair,
            help='key=value pair. Multiple --setting arguments may be'
                 ' specified.')

        subparsers = self.getParser().add_subparsers(
            title='subcommands',
            description='valid subcommands',
            help='additional help',
            dest='subparser_name')

        # settings
        settings_args = argparse.ArgumentParser(add_help=False)
        settings_args.add_argument(
            '--resource-adapter', '-r', metavar='NAME', required=True,
            help='Resource adapter name')
        settings_args.add_argument(
            '--optional', '-o', dest='show_optional', required=False,
            action='store_true', default=False,
            help='Display optional settings')
        settings_args.add_argument(
            '--advanced', '-v', dest='show_advanced', required=False,
            action='store_true', default=False,
            help='Display advanced settings')
        subparsers.add_parser('settings', parents=[settings_args])

        # show
        show_args = argparse.ArgumentParser(add_help=False)
        show_args.add_argument(
            '--resource-adapter', '-r', metavar='NAME', required=True,
            help='Resource adapter name')
        show_args.add_argument(
            '--profile', '-p', metavar='NAME', required=True,
            help='Configuration profile name')
        show_args.add_argument(
            '--all', dest='show_all', required=False, action='store_true',
            default=False,
            help='Display all settings, including passwords/keys')
        show_args.add_argument(
            '--setting', '-s', metavar='KEY',
            help='Display specified setting only')
        subparsers.add_parser('show',
                              parents=[show_args, show_list_common_args])

        validate_args = argparse.ArgumentParser(add_help=False)
        validate_args.add_argument(
            '--resource-adapter', '-r', metavar='NAME', required=True,
            help='Resource adapter name')
        validate_args.add_argument(
            '--profile', '-p', metavar='NAME', required=True,
            help='Configuration profile name')
        subparsers.add_parser('validate', parents=[validate_args])

        # create
        create_args = argparse.ArgumentParser(add_help=False)
        create_args.add_argument(
            '--profile', '-p', metavar='NAME',
            help='Configuration profile name', required=True)
        subparsers.add_parser('create',
                              parents=[common_args, create_args,
                                       show_list_common_args,
                                       create_update_common_args])

        # copy
        subparser_copy = subparsers.add_parser('copy')

        subparser_reqd_arguments_group = subparser_copy.add_argument_group(
            'required arguments')

        subparser_reqd_arguments_group.add_argument(
            '--resource-adapter', '-r', metavar='NAME', required=True,
            help='Resource adapter name')
        subparser_reqd_arguments_group.add_argument(
            '--profile', '-p', metavar='NAME', required=True,
            help='Configuration profile name')

        subparser_reqd_arguments_group.add_argument(
            '--src', metavar='NAME',
            required=True, help='Source configuration profile name')

        # import
        subparser_import = subparsers.add_parser(
            'import', parents=[common_args])
        subparser_import.add_argument('--force', action='store_true')

        group = subparser_import.add_mutually_exclusive_group(required=True)

        group.add_argument(
            '--json-file', metavar='FILENAME', type=argparse.FileType('r'),
            help='Import from JSON formatted file')

        group.add_argument(
            '--adapter-config', metavar='FILENAME',
            type=argparse.FileType('r'),
            help='Import from legacy resource adapter configuration file')

        # export
        subparsers.add_parser('export', parents=[common_args])

        # list
        subparsers.add_parser(
            'list', parents=[common_args, show_list_common_args])

        # delete
        self.subparser_delete = subparsers.add_parser(
            'delete', parents=[common_args])

        self.subparser_delete.add_argument(
            '--profile', '-p', metavar='NAME',
            help='Configuration profile name', required=True)

        self.subparser_delete.add_argument(
            '--force', '-f', action='store_true', default=False,
            help='Do not prompt when deleting profile')

        # update
        update_args = argparse.ArgumentParser(add_help=False)
        update_args.add_argument(
            '--profile', '-p', metavar='NAME',
            help='Configuration profile name', required=True)
        self.subparser_update = subparsers.add_parser(
            'update',
            parents=[common_args, update_args, create_update_common_args])

        self.subparser_update.add_argument(
            '--delete-setting', '-d', metavar="KEY", type=cfgkey,
            action='append', help='Delete specified setting from profile')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(usage='Manage Tortuga resource adapter configuration')

        args = self.getParser().parse_args()

        self.api = ResourceAdapterConfigurationWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl(),
            verify=self._verify
        )

        if not hasattr(
                self,
                '{0}_resource_adapter_config'.format(args.subparser_name)):
            raise NotImplementedError(
                'Handler for action [{0}] not implemented'.format(
                    args.subparser_name))

        handler = getattr(
            self, '{0}_resource_adapter_config'.format(args.subparser_name))

        handler(args)

    def list_resource_adapter_config(self, args):
        try:
            cfg = self.api.get_profile_names(args.resource_adapter)

            if args.json:
                sys.stdout.write(json.dumps(cfg))
            else:
                if cfg:
                    sys.stdout.write('\n'.join(cfg) + '\n')

            sys.stdout.flush()
        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def show_resource_adapter_config(self, args):
        try:
            cfg = self.api.get(args.resource_adapter, args.profile)

            if args.setting:
                self._show_resource_adapter_config_setting(cfg, args.setting)

            elif args.json:
                self._show_resource_adapter_config_json(cfg)

            else:
                self._show_resource_adapter_config_stdout(cfg, args.show_all)

        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def _show_resource_adapter_config_setting(self, cfg: dict, name: str):
        for cfgitem in cfg['configuration']:
            if cfgitem['key'] == name:
                sys.stdout.write(cfgitem['value'] + '\n')
                return

        sys.stderr.write('Error: setting does not exist: {}\n'.format(name))
        sys.exit(1)

    def _show_resource_adapter_config_json(self, cfg: dict):
        sys.stdout.write(json.dumps(cfg))
        sys.stdout.flush()

    def _show_resource_adapter_config_stdout(self, cfg: dict,
                                             show_all: bool = False):
        sys.stdout.write(
            'Resource adapter: {}\n'.format(
                cfg['resourceadapter']['name']))

        sys.stdout.write('Profile: {}\n'.format(cfg['name']))

        if not cfg['configuration']:
            return

        sys.stdout.write('Configuration:\n')

        ra_settings = cfg['resourceadapter']['settings']

        for cfgitem in cfg['configuration']:
            key = cfgitem['key']

            setting = ra_settings.get(key, {})
            is_secret = setting.get('secret', False)

            value = cfgitem['value']
            if not show_all and is_secret:
                value = '<REDACTED>'

            sys.stdout.write('  - {} = {}\n'.format(key, value))

    def validate_resource_adapter_config(self, args):
        try:
            validation: dict = self.api.validate(args.resource_adapter,
                                                 args.profile)

            sys.stdout.write(
                'Resource adapter: {}\n'.format(args.resource_adapter))
            sys.stdout.write('Profile: {}\n'.format(args.profile))

            if not validation:
                sys.stdout.write('No errors found\n')
                return

            sys.stdout.write('Errors:\n')

            for k, v in validation.items():
                sys.stdout.write('  - {}: {}\n'.format(k, v))

        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def settings_resource_adapter_config(self, args):
        ra = self._get_resource_adapter(args.resource_adapter)

        sys.stdout.write('Resource adapter: {}\n'.format(ra['name']))

        settings = ra.get('settings', {})
        if not settings:
            sys.stdout.write('No settings available\n')
            return

        sys.stdout.write('Required:\n')
        required_found = False

        for name, setting in settings.items():
            if not setting.get('required', False):
                continue
            required_found = True
            self._print_setting(name, setting)

        if not required_found:
            print('  No required settings')

        if args.show_optional:
            optional_found = False
            sys.stdout.write('Optional:\n')

            for name, setting in settings.items():
                if setting.get('required', False) or \
                        setting.get('advanced', False):
                    continue
                optional_found = True
                self._print_setting(name, setting)

            if not optional_found:
                print('  No optional settings available')

        if args.show_advanced:
            advanced_found = False
            sys.stdout.write('Advanced:\n')

            for name, setting in settings.items():
                if not setting.get('advanced', False):
                    continue
                advanced_found = True
                self._print_setting(name, setting)

            if not advanced_found:
                print('  No advanced settings available')

    def _get_resource_adapter(self, name: str) -> Optional[dict]:
        """
        Gets a resource adapter definition by name.

        :param str name: the resource adapter name

        :return dict:    a dict containing the resource adapter definition,
                         if found otherwise None

        """
        ra_api = ResourceAdapterWsApi(
            username=self.getUsername(),
            password=self.getPassword(),
            baseurl=self.getUrl(),
            verify=self._verify
        )

        ra_list = ra_api.getResourceAdapterList()
        for ra in ra_list:
            if ra['name'] == name:
                return ra

        return {}

    def _print_setting(self, name: str, setting: dict):
        sys.stdout.write('  - {}:\n'.format(name))

        output: dict = dict()

        if setting.get('description', None):
            output['Description'] = setting['description']

        output['Type'] = setting.get('type', 'string')

        if setting.get('base_path', None):
            output['Base path'] = setting['base_path']

        if setting.get('must_exist', None) is not None:
            output['Must exist'] = "yes" if setting['must_exist'] else "no"

        if setting.get('list', False):
            output['List'] = 'yes, using "{}" as a separator'.format(
                setting.get('list_separator', ', '))

        if setting.get('values', []):
            output['Values'] = ', '.join(setting['values'])

        if setting.get('default', None):
            output['Default'] = setting['default']

        if setting.get('requires', []):
            output['Requires'] = ', '.join(setting['requires'])

        if setting.get('mutually_exclusive', []):
            output['Mutually exclusive'] = \
                ', '.join(setting['mutually_exclusive'])

        sys.stdout.write(self._format_output(output))

    def _format_output(self, output: dict) -> str:
        if not output:
            return ''

        longest_key = 0
        for k in output.keys():
            if len(k) > longest_key:
                longest_key = len(k)

        formatted_output = ''
        for k, v in output.items():
            space = ' ' * (longest_key - len(k))
            formatted_output += '      {}:{} {}\n'.format(k, space, v)

        return formatted_output

    def create_resource_adapter_config(self, args):
        try:
            cfg = [dict(key=key, value=value)
                   for key, value in args.setting] if args.setting else None

            self.api.create(args.resource_adapter, args.profile, cfg)
        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def copy_resource_adapter_config(self, args):
        try:
            src_cfg = self.api.get(args.resource_adapter, args.src)

            self.api.create(args.resource_adapter, args.profile,
                            src_cfg['configuration'])
        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def delete_resource_adapter_config(self, args):
        try:
            if not args.force:
                sys.stdout.write(
                    'Are you sure you want to delete configuration profile {0}'
                    ' for resource adapter {1} [N/y]? '.format(
                        args.profile, args.resource_adapter))

                response = input('')

                if not response.lower().startswith('y'):
                    sys.stderr.write('Aborted by user.\n')
                    sys.stderr.flush()
                    sys.exit(1)

            self.api.delete(args.resource_adapter, args.profile)
        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def update_resource_adapter_config(self, args):
        if args.setting is None and args.delete_setting is None:
            self.subparser_update.error(
                'arguments --setting/-s and/or'
                ' --delete-setting/-d are required')

        if args.verbose:
            sys.stdout.write(
                'Updating resource adapter [{0}] profile [{1}]...\n'.format(
                    args.resource_adapter, args.profile))
            sys.stdout.flush()

        try:
            cfg: List[Dict[str, str]] = []

            for key, value in args.setting or []:
                if args.verbose:
                    sys.stdout.write(
                        '  - updating setting [{0}]\n'.format(key))
                    sys.stdout.flush()

                cfg.append(dict(key=key, value=value))

            for delete_key in args.delete_setting or []:
                if args.verbose:
                    sys.stdout.write(
                        '  - deleting setting [{0}]\n'.format(delete_key))
                    sys.stdout.flush()

                cfg.append(dict(key=delete_key, value=None))

            self.api.update(args.resource_adapter, args.profile, cfg)

            if args.verbose:
                sys.stdout.write('Done.\n')
                sys.stdout.flush()
        except TortugaException as exc:
            sys.stderr.write('Error: {0}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def import_resource_adapter_config(self, args):
        if args.json_file:
            self.__import_json_file(args)
        elif args.adapter_config:
            self.__import_resource_adapter_config(args)

    def __import_json_file(self, args):
        # Import from JSON'
        cfg = json.load(args.json_file)

        profile_name = cfg['name']

        # Check if profile already exists
        try:
            self.api.get(args.resource_adapter, profile_name)

            profile_exists = True
        except ResourceNotFound:
            # This is good!
            pass

        try:
            if profile_exists and not args.force:
                _raise_profile_already_exists(
                    args.resource_adapter, profile_name)

            # Deleting existing profile
            self.api.delete(args.resource_adapter, profile_name)

            self.api.create(
                args.resource_adapter, profile_name, cfg['configuration'])
        except TortugaException as exc:
            sys.stderr.write('Error: {}\n'.format(exc))
            sys.stderr.flush()
            sys.exit(1)

    def __import_resource_adapter_config(self, args):
        # Import from legacy resource adapter configuration file
        cfg = configparser.ConfigParser()

        sys.stdout.write('Processing resource adapter configuration... ')
        sys.stdout.flush()

        cfg.read_file(args.adapter_config)

        sys.stdout.write('done.\n')
        sys.stdout.flush()

        delete_profiles = []

        profile_names = [name
                         if name != 'resource-adapter' else 'Default'
                         for name in cfg.sections()]

        # Ensure profile name(s) do not already exist
        sys.stdout.write(
            'Checking for existing (conflicting) profiles... ')
        sys.stdout.flush()

        for profile_name in profile_names:
            try:
                self.api.get(args.resource_adapter, profile_name)

                if not args.force:
                    sys.stdout.write('done.\n')
                    sys.stdout.flush()

                    _raise_profile_already_exists(
                        args.resource_adapter, profile_name)

                # Append profile to be deleted prior to importing
                delete_profiles.append(profile_name)
            except (ResourceAdapterNotFound, ResourceNotFound):
                pass

        sys.stdout.write('done.\n')
        sys.stdout.flush()

        # Delete any conflicting profiles. 'delete_profiles' only defined
        # if --force specified.
        if delete_profiles:
            for profile_name in delete_profiles:
                sys.stdout.write(
                    'Deleting existing profile [{0}]... '.format(
                        profile_name))
                sys.stdout.flush()

                self.api.delete(args.resource_adapter, profile_name)

                sys.stdout.write('done.\n')
                sys.stdout.flush()

        for section_name in cfg.sections():
            profile_name = section_name \
                if section_name != 'resource-adapter' else 'Default'

            configuration = []

            for name, value in cfg.items(section_name):
                if not value:
                    sys.stdout.write(
                        '* skipping empty setting [{0}] in'
                        ' section [{1}]\n'.format(name, profile_name))
                    sys.stdout.flush()

                    continue

                configuration.append(dict(key=name, value=value))

            sys.stdout.write(
                'Creating profile [{0}] for resource adapter'
                ' [{1}]... '.format(profile_name, args.resource_adapter))
            sys.stdout.flush()

            self.api.create(
                args.resource_adapter, profile_name, configuration)

            sys.stdout.write('done.\n')
            sys.stdout.flush()

        sys.stdout.write('Import completed successfully.\n')
        sys.stdout.flush()

    def export_resource_adapter_config(self, args):
        dstfile = 'adapter-defaults-{0}.conf'.format(args.resource_adapter)

        if os.path.exists(dstfile):
            sys.stderr.write(
                'Error: file {0} already exists. Will not'
                ' overwrite.\n'.format(dstfile))

            sys.exit(1)

        output = configparser.ConfigParser()

        for profile_name in \
                self.api.get_profile_names(args.resource_adapter):
            section = profile_name \
                if profile_name != 'Default' else 'resource-adapter'

            output.add_section(section)

            for cfg_item in self.api.get(
                    args.resource_adapter, profile_name)['configuration']:
                key = cfg_item['key']
                value = cfg_item['value']
                output.set(section, key, value)

        with open(dstfile, 'w') as fp:
            output.write(fp)


def key_value_pair(arg):
    key, value = arg.split('=', 1)

    return key, value


def cfgkey(arg):
    return arg


def _raise_profile_already_exists(adapter_name, profile_name):
    raise ResourceAlreadyExists(
        'Profile [{0}] already exists for resource adapter'
        ' [{1}]'.format(profile_name, adapter_name))


def main():
    AdapterMgmtCLI().run()
