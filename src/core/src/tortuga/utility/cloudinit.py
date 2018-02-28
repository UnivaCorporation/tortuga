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
import yaml
from tortuga.config.configManager import ConfigManager


def get_cloud_init_path(hostname):
    '''
    Returns path to per-host cloud-init script(s)
    '''

    return os.path.join(
        ConfigManager().getTortugaIntWebRoot(),
        'cloud-init',
        hostname)


def dump_cloud_config_yaml(user_data):
    '''
    Dump dict to cloud-init compatible YAML
    '''

    return'#cloud-config\n\n' + yaml.dump(
        user_data, explicit_start=False, default_flow_style=False)
