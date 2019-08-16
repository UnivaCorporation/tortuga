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
import os

from tortuga.kit.actions import ComponentActionBase


class GetPuppetArgsAction(ComponentActionBase):
    def do_action(self, db_software_profile, db_hardware_profile,
                  *args, **kwargs):
        db_engine = self.kit_installer.config_manager.get_database_engine()

        return {
            'proxy_hash': self._get_proxy_hash(),
            'database_engine': db_engine,
        }

    def _get_proxy_hash(self):
        config_parser = configparser.ConfigParser()
        config_parser.read(
            os.path.join(
                self.kit_installer.config_manager.getKitConfigBase(),
                'base/apache-component.conf'
            )
        )

        proxy_list = config_parser.get('proxy', 'proxy_list').split(' ') \
            if config_parser.has_section('proxy') and \
            config_parser.has_option('proxy', 'proxy_list') else []

        #
        # Generate a dict of proxy settings to be passed into Puppet
        # class.
        #
        proxy_dict = {}
        for proxy_path in proxy_list:
            if not config_parser.has_option('proxy', proxy_path):
                #
                # Skip malformed entry
                #
                continue

            proxy_url = config_parser.get('proxy', proxy_path)

            if not proxy_url:
                #
                # Skip malformed entry
                #
                continue

            proxy_dict[proxy_path] = {
                'path': proxy_path,
                'url': proxy_url,
            }

        return proxy_dict
