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

from tortuga.kit.installer import KitInstallerBase
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi, Parameter
from tortuga.exceptions.parameterNotFound import ParameterNotFound

from .actions.post_install import PostInstallAction


class BaseKitInstaller(KitInstallerBase):
    puppet_modules = ['univa-tortuga_kit_base']

    def __init__(self):
        self._global_param_db_api = GlobalParameterDbApi()
        super().__init__()

    def get_db_parameter_value(self, key, default='__throw_exception__'):
        try:
            return self._global_param_db_api.getParameter(key).getValue()
        except ParameterNotFound:
            if default == '__throw_exception__':
                raise
        return default

    def get_db_parameter_bool(self, key, default='__throw_exception__'):
        value = self.get_db_parameter_value(key, default)
        return bool(value[0] == '1')

    def set_db_parameter_value(self, key, value):
        self._global_param_db_api.addParameter(Parameter(name=key,
                                                         value=value))

    def action_post_install(self):
        super().action_post_install()
        return PostInstallAction(self)()
