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

from logging import getLogger
import os
import sys


from .registry import discover_kit_installers
from tortuga.config.configManager import ConfigManager


logger = getLogger(__name__)


def load_kits():
    """
    Loads all installed kit installers.

    """
    config_manager = ConfigManager()
    kits_dir = config_manager.getKitDir()
    kits_dir_list = os.listdir(config_manager.getKitDir())
    for entry in kits_dir_list:
        kit_search_path = os.path.join(kits_dir, entry)
        if not os.path.isdir(kit_search_path):
            continue
        kit_meta_path = os.path.join(kit_search_path, 'kit.json')
        if os.path.exists(kit_meta_path):
            if kit_search_path not in sys.path:
                logger.debug(
                    'Adding kit search path to sys.path: {}'.format(
                        kit_search_path))
                sys.path.insert(0, kit_search_path)
    discover_kit_installers()
