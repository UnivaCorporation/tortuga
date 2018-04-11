#!/usr/bin/env python

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
from tortuga.wsapi.nodeWsApi import NodeWsApi


class TransferNodeCli(TortugaCli):
    """
    Transfer node command line interface.
    """

    def parseArgs(self, usage=None):
        self.addOption(
            '--node', dest='nodeName',
            help=_('Name of node to transfer'))
        self.addOption(
            '--count', dest='nodeCount',
            help=_('Number of nodes to transfer'), type=int)
        self.addOption(
            '--src-software-profile',
            dest='srcSoftwareProfileName',
            help=_('Source software profile to transfer nodes from'))
        self.addOption(
            '--software-profile', dest='softwareProfileName',
            help=_('Destination software profile to transfer node to'))

        self.addOption(
            '--force', dest='force', action='store_true', default=False,
            help=_('Force node transfer regardless of node state'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs('''
Transfer nodes from one software profile to
another. This operation may need a reinstall of the node to apply
the new software profile.
''')

        nodeName = self.getArgs().nodeName
        nodeCount = self.getArgs().nodeCount
        dstSoftwareProfileName = self.getArgs().softwareProfileName
        srcSoftwareProfileName = self.getArgs().srcSoftwareProfileName

        if not dstSoftwareProfileName:
            self.usage(_('Missing --software-profile option'))

        if nodeName:
            if nodeCount:
                self.usage(_("Can't use --count option with --node option"))
            if srcSoftwareProfileName:
                self.usage(
                    _("Can't use --src-software-profile option with"
                      " --node option"))

        if not nodeName:
            if not nodeCount:
                self.usage(
                    _("Must use --count option when not using --node"
                      " option"))

            # if not srcSoftwareProfileName:
            #     self.usage(
            #         _("Must use --src-software-profile option when not"
            #           " using --node option"))

        api = NodeWsApi(username=self.getUsername(),
                        password=self.getPassword(),
                        baseurl=self.getUrl())

        if nodeName:
            api.transferNode(
                nodeName, dstSoftwareProfileName,
                bForce=self.getArgs().force)
        else:
            # Transfer 1 or more nodes from a source software profile
            api.transferNodes(
                srcSoftwareProfileName, dstSoftwareProfileName, nodeCount,
                bForce=self.getArgs().force)


def main():
    TransferNodeCli().run()
