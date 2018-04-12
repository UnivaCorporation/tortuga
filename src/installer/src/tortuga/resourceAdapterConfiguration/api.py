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

from ..utility.tortugaApi import TortugaApi
from .manager import ResourceAdapterConfigurationManager


class ResourceAdapterConfigurationApi(TortugaApi):
    def create(self, session, resadapter_name, name, configuration):
        self.getLogger().debug(
            'create(resadapter_name=[{}], name=[{}],'
            ' configuration=[...])'.format(resadapter_name, name))

        ResourceAdapterConfigurationManager().create(
            session, resadapter_name, name, configuration)

    def get(self, session, resadapter_name, name):
        self.getLogger().debug(
            'get(resadapter_name=[{}], name=[{}])'.format(
                resadapter_name, name))

        return ResourceAdapterConfigurationManager().get(
            session, resadapter_name, name)

    def get_profile_names(self, session, adapter_name):
        self.getLogger().debug('get_profile_names()')
        return ResourceAdapterConfigurationManager().get_profile_names(
            session, adapter_name)

    def delete(self, session, resadapter_name, name):
        self.getLogger().debug(
            'delete(resadapter_name=[{}], name=[{}])'.format(
                resadapter_name, name))

        ResourceAdapterConfigurationManager().delete(
            session, resadapter_name, name)

    def update(self, session, resadapter_name, name, configuration):
        self.getLogger().debug(
            'update(resadapter_name=[{}], name=[{}],'
            ' configuration=[...])'.format(resadapter_name, name))

        ResourceAdapterConfigurationManager().update(
            session, resadapter_name, name, configuration)
