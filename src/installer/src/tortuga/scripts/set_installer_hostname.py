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

import os
import socket
from typing import Optional

import yaml

from sqlalchemy.orm.exc import NoResultFound
from tortuga.cli.tortugaCli import TortugaCli
from tortuga.db.dbManager import DbManager
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.exceptions.operationFailed import OperationFailed


class SetInstallerHostNameCLI(TortugaCli):
    HIERA_PATH = '/etc/puppetlabs/code/environments/production/data/tortuga-common.yaml'

    def parseArgs(self, usage: Optional[str] = None) -> None:
        self.addOption('--public', action='store_true', default=False,
                       help='Set installer public host name')

        self.getParser().add_argument('hostname', metavar='HOSTNAME',
                                      type=str, nargs=1,
                                      help='Host name')

        super().parseArgs(usage=usage)

    def runCommand(self) -> None:
        self.parseArgs()

        with DbManager().session() as session:
            try:
                installer_swprofile = session.query(SoftwareProfile).filter(
                    SoftwareProfile.type == 'installer').first()
            except NoResultFound:
                raise OperationFailed(
                    'Malformed installation: no installer software profile'
                    ' found')

            installer_node = installer_swprofile.nodes[0]
            host_name_arg = self.getArgs().hostname[0]
            write_to_hiera = False

            if self.getArgs().public:
                installer_node.public_hostname = host_name_arg
                write_to_hiera = True

            else:
                installer_node.name = host_name_arg

            session.commit()

            if write_to_hiera:
                self._write_to_hiera(host_name_arg)

    def _write_to_hiera(self, hostname: str):
        hiera_vars = {}

        if os.path.exists(self.HIERA_PATH):
            with open(self.HIERA_PATH) as fp:
                hiera_vars = yaml.load(fp)

        hiera_vars['installer_public_hostname'] = hostname
        hiera_vars['installer_public_ip'] = socket.gethostbyname(hostname)

        with open(self.HIERA_PATH, 'w') as fp:
            fp.write('---\n')
            yaml.safe_dump(hiera_vars, fp, default_flow_style=False)


def main():
    SetInstallerHostNameCLI().run()
