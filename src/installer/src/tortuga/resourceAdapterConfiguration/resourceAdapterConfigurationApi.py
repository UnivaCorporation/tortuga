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

# pylint: disable=no-member

from .resourceAdapterConfigurationManager \
    import ResourceAdapterConfigurationManager


class ResourceAdapterConfigurationApi:
    def create(self, resadapter_name, name, configuration):
        self.getLogger().debug(
            '[{0}] create(resadapter_name=[{1}], name=[{2}],'
            ' configuration=[...])'.format(
                self.__class__.__name__, resadapter_name, name))

        ResourceAdapterConfigurationManager().create(
            resadapter_name, name, configuration)

    def get(self, resadapter_name, name):
        self.getLogger().debug(
            '[{0}] get(resadapter_name=[{1}], name=[{2}])'.format(
                self.__class__.__name__, resadapter_name, name))

        return ResourceAdapterConfigurationManager().get(resadapter_name, name)

    def get_profile_names(self, adapter_name):
        return ResourceAdapterConfigurationManager().get_profile_names(
            adapter_name)

    def delete(self, resadapter_name, name):
        self.getLogger().debug(
            '[{0}] delete(resadapter_name=[{1}], name=[{2}])'.format(
                self.__class__.__name__, resadapter_name, name))

        ResourceAdapterConfigurationManager().delete(resadapter_name, name)

    def update(self, resadapter_name, name, configuration):
        self.getLogger().debug(
            '[{0}] update(resadapter_name=[{1}], name=[{2}],'
            ' configuration=[...])'.format(
                self.__class__.__name__, resadapter_name, name))

        ResourceAdapterConfigurationManager().update(
            resadapter_name, name, configuration)
