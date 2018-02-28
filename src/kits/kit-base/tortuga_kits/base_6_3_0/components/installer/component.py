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

import configparser
from logging import getLogger
import os
import tempfile

from .actions.get_puppet_args import GetPuppetArgsAction
from tortuga.kit.installer import ComponentInstallerBase
from tortuga.os_utility import tortugaSubprocess

logger = getLogger(__name__)


class ComponentInstaller(ComponentInstallerBase):
    name = 'installer'
    version = '6.3.0'
    os_list = [
        {'family': 'rhel', 'version': '6', 'arch': 'x86_64'},
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]

    installer_only = True

    def run_script(self, action, software_profiles, nodes=None):
        script_path = self._get_host_action_hook_script()

        if script_path is None:
            return

        cmd = '{} --action {}'.format(script_path, action)

        if software_profiles:
            cmd += ' --software-profiles {}'.format(
                ','.join(software_profiles))

        tmp_file_to_delete = None

        if nodes:
            fh, tmp_file_name = self._get_tmp_file()
            os.write(fh, '\n'.join(nodes))
            os.close(fh)
            cmd += ' --nodes {}'.format(tmp_file_name)
            tmp_file_to_delete = tmp_file_name

        tortugaSubprocess.executeCommand(cmd)

        if tmp_file_to_delete:
            os.unlink(tmp_file_to_delete)

    def _get_host_action_hook_script(self):
        config_parser = configparser.ConfigParser()

        file_name = os.path.join(
            self.kit_installer.config_manager.getKitConfigBase(),
            'tortuga.ini'
        )
        if not os.path.exists(file_name):
            logger.debug('Configuration file not found: {}'.format(file_name))
            return None

        config_parser.read(file_name)

        if not config_parser.has_section('installer'):
            return None

        if not config_parser.has_option('installer',
                                        'host_action_hook_script'):
            logger.debug(
                'host_action_hook_script not defined, ignoring')
            return

        script_path = config_parser.get('installer',
                                        'host_action_hook_script')

        script_path = script_path.replace(
            '$TORTUGA_ROOT', self.kit_installer.config_manager.getRoot())

        if not os.path.exists(script_path):
            logger.debug(
                'Node hook script does not exist: {}'.format(script_path))
            return None

        if not os.access(script_path, os.X_OK):
            logger.debug(
                'Node host script is not executable: {}'.format(script_path))
            return None

        return script_path

    def _get_tmp_file(self):
        tmp_dir = os.path.join(self.kit_installer.config_manager.getRoot(),
                               'var/tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, 700)
        return tempfile.mkstemp(dir=tmp_dir)

    def action_add_host(self, hardware_profile_name, software_profile_name,
                        nodes, *args, **kwargs):
        node_name_list = [n.getName() for n in nodes]
        self.run_script(
            'add', software_profiles=[software_profile_name],
            nodes=node_name_list
        )

    def action_delete_host(self, hardware_profile_name, software_profile_name,
                           nodes, *args, **kwargs):
        self.run_script(
            'delete',
            software_profiles=[software_profile_name],
            nodes=nodes
        )

    def action_get_puppet_args(self, db_software_profile,
                               db_hardware_profile):
        return GetPuppetArgsAction(self.kit_installer, self)(
            db_software_profile, db_software_profile
        )

    def action_refresh(self, software_profile_list, *args, **kwargs):
        self.run_script('refresh', software_profiles=software_profile_list)
