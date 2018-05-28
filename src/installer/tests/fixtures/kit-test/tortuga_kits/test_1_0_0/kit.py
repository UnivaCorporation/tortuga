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

from typing import Optional

from tortuga.kit.installer import KitInstallerBase


class ExampleKitInstaller(KitInstallerBase):
    #
    # If your kit requires the installation of puppet modules (from the
    # puppet_modules directory), list them here.
    #
    puppet_modules = []

    def action_pre_install(self):
        """
        This hook is invoked on the installer prior to installing the
        kit.

        """
        pass

    def action_pre_uninstall(self):
        """
        This hook is invoked on the installer prior to uninstalling the
        kit.

        """
        pass

    def action_post_install(self):
        """
        This hook is invoked on the installer after installing the kit.
        The default behavior for this hook is to install any python
        packages found in the kit's requirements.txt file. If you want
        to maintain this behavior, make sure to call the superclass
        method.

        """
        super().action_post_install()

    def action_post_uninstall(self):
        """
        This hook is invoked on the installer after uninstalling the kit.

        """
        pass

    def action_get_metadata(self,
                            hardware_profile_name: Optional[str] = None,
                            software_profile_name: Optional[str] = None,
                            node_name: Optional[str] = None) -> dict:
        """
        This hook is invoked to query for read-only metadata related to the
        specified object(s).

        """
        pass
