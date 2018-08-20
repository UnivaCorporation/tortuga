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

from ..installer import ComponentInstallerBase, KitInstallerBase


class KitActionBase:
    def __init__(self, kit_installer: KitInstallerBase):
        self.kit_installer = kit_installer

    def is_runnable(self, *args, **kwargs):
        """
        Tests to see if this action is runnable.

        :param args:
        :param kwargs:

        :return: True if it is runnable, false otherwise

        """
        return True

    def do_action(self, *args, **kwargs):
        """
        Does the action. Override this in your implementations.

        """
        pass

    def __call__(self, *args, **kwargs):
        """
        Runs this action.

        """
        if self.is_runnable(*args, **kwargs):
            return self.do_action(*args, **kwargs)



class ComponentActionBase:
    def __init__(self, kit_installer: KitInstallerBase,
                 component_installer: ComponentInstallerBase):
        self.kit_installer = kit_installer
        self.component_installer = component_installer

    def is_runnable(self, *args, **kwargs):
        """
        Tests to see if this action is runnable.

        :return: True if it is runnable, false otherwise

        """
        return True

    def do_action(self, *args, **kwargs):
        """
        Does the action. Override this in your implementations.

        """
        pass

    def __call__(self, *args, **kwargs):
        """
        Runs this action.

        """
        if self.is_runnable(*args, **kwargs):
            return self.do_action(*args, **kwargs)
