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

import argparse

from tortuga.cli.base import RootCommand
from tortuga.cli.utils import pretty_print
from ..script import ConfigException, TortugaScriptConfig,\
    TortugaScriptConfigSchema


class ConfigCommand(RootCommand):
    """
    Config command for displaying current CLI config.

    """
    name = 'config'
    help = 'Display the current CLI configuration'

    def execute(self, args: argparse.Namespace):
        """
        Print the current CLI configuration to stdout.

        """
        config: TortugaScriptConfig = self.get_config()
        schema = TortugaScriptConfigSchema()
        config_data = schema.dump(config).data
        try:
            config_data['auth_method'] = config.get_auth_method()
        except ConfigException:
            pass
        pretty_print(config_data, args.fmt)
