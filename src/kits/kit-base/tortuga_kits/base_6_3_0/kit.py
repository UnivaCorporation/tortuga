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
