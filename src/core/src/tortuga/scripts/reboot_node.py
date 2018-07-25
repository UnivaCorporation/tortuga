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

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.nodeWsApi import NodeWsApi


class RebootNodeCli(TortugaCli):
    def parseArgs(self, usage=None):
        optionGroupName = _('Reboot Node Options')

        self.addOptionGroup(optionGroupName, '')

        self.addOptionToGroup(
            optionGroupName, '--node', metavar='NODESPEC', dest='nodeSpec',
            required=True, help=_('Name of node to reboot'))

        self.addOptionToGroup(
            optionGroupName, '--reinstall', dest='bReinstall',
            action='store_true', default=False,
            help=_('Toggle reinstallation of specified nodes'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_("""
Reboots specified node(s). Mark nodes for reinstallation if --reinstall
flag is specified.
"""))

        nodeApi = NodeWsApi(username=self.getUsername(),
                            password=self.getPassword(),
                            baseurl=self.getUrl(),
                            verify=self._verify)

        # If the node is being reinstalled as a result of the reboot,
        # do not use a soft shutdown.
        bSoftReboot = not self.getArgs().bReinstall

        try:
            nodeApi.rebootNode(
                self.getArgs().nodeSpec, bSoftReboot,
                bReinstall=self.getArgs().bReinstall)
        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't reboot node(s) - %s") % (msg))


def main():
    RebootNodeCli().run()
