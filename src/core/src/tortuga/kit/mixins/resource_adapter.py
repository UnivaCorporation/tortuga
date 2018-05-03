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
from tortuga.exceptions.invalidActionRequest import InvalidActionRequest
from tortuga.exceptions.resourceAdapterAlreadyExists import \
    ResourceAdapterAlreadyExists
from tortuga.hardwareprofile.hardwareProfileFactory import \
    getHardwareProfileApi
from tortuga.kit.installer import ComponentInstallerBase
from ..utils import pip_install_requirements


logger = getLogger(__name__)


class ResourceAdapterMixin:
    config_files = []
    resource_adapter_name = None

    def _get_kit_id(self):
        for kit in KitDbApi().getKitList():
            if kit.getName() == self.name:
                break
        else:
            raise InvalidActionRequest(
                'Unable to find kit: {}'.format(self.name))
        return kit.getId()

    def register_resource_adapter(self):
        resource_adapter_api = ResourceAdapterDbApi()
        kit_id = self._get_kit_id()
        try:
            resource_adapter_api.addResourceAdapter(
                self.resource_adapter_name,
                kit_id
            )
        except ResourceAdapterAlreadyExists:
            #
            # We can assume the adapter registered with the same
            # name is valid...
            #
            logger.info('Resource adapter already registered, skipping')
            pass

    def unregister_resource_adapter(self):
        resource_adapter_api = ResourceAdapterDbApi()
        resource_adapter_api.deleteResourceAdapter(self.resource_adapter_name)

    def action_post_install(self, *args, **kwargs):
        super().action_post_install(*args, **kwargs)
        #
        # Install files to '$TORTUGA_ROOT/config' directory
        #
        for config_file in self.config_files:
            src_file = os.path.join(
                self.files_path,
                config_file
            )
            dst_file = os.path.join(
                self.config_manager.getKitConfigBase(),
                config_file
            )

            #
            # Prevent existing file from being overwritten
            #
            if os.path.exists(dst_file):
                dst_file += '.new'

            logger.info(
                'Writing file: {}'.format(dst_file))

            shutil.copy2(src_file, dst_file)

    def action_post_uninstall(self, *args, **kwargs):
        super().action_post_uninstall(*args, **kwargs)
        for config_file in self.config_files:
            src_file = os.path.join(
                self.config_manager.getKitConfigBase(),
                config_file)

            #
            # This conditional should always pass, but just in case...
            # These files are installed by default.
            #
            if os.path.exists(src_file):
                shutil.copy2(src_file, src_file + '.saved')
                os.unlink(src_file)


class ResourceAdapterManagementComponentInstaller(ComponentInstallerBase):
    installer_only = True

    def action_enable(self, software_profile_name, *args, **kwargs):
        super().action_enable(software_profile_name, *args, **kwargs)
        #
        # Install required python packages from requirements.txt
        #
        requirements_path = os.path.join(
            self.component_path,
            'requirements.txt'
        )
        pip_install_requirements(self.kit_installer, requirements_path)

    def action_post_enable(self, software_profile_name, *args, **kwargs):
        super().action_post_enable(software_profile_name, *args, **kwargs)
        self.kit_installer.register_resource_adapter()

    def action_pre_disable(self, software_profile_name, *args, **kwargs):
        super().action_pre_disable(software_profile_name, *args, **kwargs)
        self._unregister_resource_adapter()

    def _unregister_resource_adapter(self):
        hardware_profile_api = getHardwareProfileApi()

        adapter_hwp_list = []

        for hardware_profile in hardware_profile_api.getHardwareProfileList(
                {'resourceadapter': True}):
            if hardware_profile.getResourceAdapter() and \
                    hardware_profile.getResourceAdapter().getName() == \
                    self.kit_installer.resource_adapter_name:
                adapter_hwp_list.append(hardware_profile)

        #
        # Ensure no nodes are using these hardware profiles
        #
        adapter_hwp_in_use = []

        for hardware_profile in adapter_hwp_list:
            nodes = hardware_profile_api.getHardwareProfile(
                hardware_profile.getName(), {'nodes': True}).getNodes()
            if nodes and hardware_profile not in adapter_hwp_in_use:
                adapter_hwp_in_use.append(hardware_profile)

        if adapter_hwp_in_use:
            print(
                'Cannot delete kit\n\n'
                'The following hardware profile(s) are using this resource '
                'adapter and have active nodes:\n'
            )

            for hardware_profile in adapter_hwp_in_use:
                print('    {}'.format(hardware_profile))
            print()

            raise InvalidActionRequest(
                'Resource adapter is still in use by at least one '
                'hardware profile')

        #
        # Unregister resource adapter
        #
        logger.info('Un-registering resource adapter: {}'.format(
            self.kit_installer.resource_adapter_name))
        self.kit_installer.unregister_resource_adapter()
