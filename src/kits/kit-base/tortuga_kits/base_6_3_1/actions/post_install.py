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
import shutil

from tortuga.db.kitDbApi import KitDbApi
from tortuga.db.resourceAdapterDbApi import ResourceAdapterDbApi
from tortuga.kit.actions import KitActionBase


logger = getLogger(__name__)


class PostInstallAction(KitActionBase):
    def do_action(self, *args, **kwargs):
        self._copy_config_files()
        self._install_default_resource_adapters()

    def _copy_config_files(self):
        file_name = 'apache-component.conf'

        src_path = os.path.join(
            self.kit_installer.files_path, file_name)
        dst_path = os.path.join(
            self.kit_installer.config_manager.getKitConfigBase(),
            'base',
            file_name)

        if os.path.exists(dst_path):
            dst_path += '.new'
        shutil.copyfile(src_path, dst_path)

        logger.debug(
            'File copied: {} -> {}'.format(src_path, dst_path))

    def _install_default_resource_adapters(self):
        """
        Installs default resource adapters.

        """
        adapters_to_install = ['default']
        installed_adapters = ResourceAdapterDbApi().getResourceAdapterList(
            self.kit_installer.session)
        for adapter in installed_adapters:
            adapter_name = adapter.getName()
            if adapter_name in installed_adapters:
                adapters_to_install.remove(adapter_name)

        if not adapters_to_install:
            return

        base_kit_id = self._get_base_kit().getId()
        for resource_adapter_name in adapters_to_install:
            ResourceAdapterDbApi().addResourceAdapter(
                self.kit_installer.session, name=resource_adapter_name,
                kitId=base_kit_id)

    def _get_base_kit(self):
        """
        Gets the base kit from the database.

        :return: a Kit instance

        """
        kit = None
        for k in KitDbApi().getKitList(self.kit_installer.session):
            if k.getName() == 'base':
                kit = k
        return kit
