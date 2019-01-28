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

import os
import pwd
import shutil

from sqlalchemy.orm.session import Session

from tortuga.config.configManager import ConfigManager
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.node import state
from tortuga.os_objects.osObjectManager import OsObjectManager


class OsBootHostManagerCommon(OsObjectManager):
    """
    Methods for manipulating PXE files
    """

    def __init__(self, configManager: ConfigManager) -> None:
        super().__init__(configManager)

        # Cache this for later
        try:
            self.passdata = pwd.getpwnam('apache')
        except KeyError:
            username = os.getenv('USER')
            if not username:
                self.passdata = pwd.getpwuid(os.getuid())
            else:
                self.passdata = pwd.getpwnam(username)

        self._cm = configManager

    def deletePuppetNodeCert(self, nodeName: str) -> None:
        # Remove the Puppet certificate when the node is reinstalled

        self._logger.debug(
            'deletePuppetNodeCert(node=[%s])' % (nodeName))

        puppetSslDir = '/etc/puppetlabs/puppet/ssl'
        puppetReportDir = '/var/lib/puppet/reports'
        puppetYamlDir = '/var/lib/puppet/yaml'

        filesToRemove = [
            os.path.join(puppetSslDir, 'public_keys/%s.pem' % (nodeName)),
            os.path.join(puppetSslDir, 'ca/signed/%s.pem' % (nodeName)),
            os.path.join(puppetSslDir, 'private_keys/%s.pem' % (nodeName)),
            os.path.join(puppetSslDir, 'certs/%s.pem' % (nodeName)),
            os.path.join(puppetYamlDir, 'node/%s.yaml' % (nodeName)),
            os.path.join(puppetYamlDir, 'facts/%s.yaml' % (nodeName)),
        ]

        for fn in filesToRemove:
            try:
                os.unlink(fn)
            except OSError as exc:
                if exc.errno != 2:
                    self._logger.error(
                        'Error attempting to remove %s (reason: %s)' % (
                            fn, exc))

        fn = os.path.join(puppetReportDir, nodeName)
        try:
            shutil.rmtree(fn)
        except OSError as exc:
            if exc.errno != 2:
                self._logger.error(
                    'Error attempting to remove %s (reason: %s)' % (
                        fn, exc))

    def nodeCleanup(self, nodeName: str):
        """
        Remove files related to the node
        """

        # Remove 'private' directory
        private_dir = os.path.join(self._cm.getRoot(), 'private', nodeName)

        if os.path.exists(private_dir):
            shutil.rmtree(private_dir)

    def addDhcpLease(self, node: Node, nic: Nic):
        # Add DHCP lease to DHCP server
        pass

    def removeDhcpLease(self, node: Node) -> None: \
            # pylint: disable=unused-argument
        # Remove the DHCP lease from the DHCP server.  This will be
        # a no-op on any platform that doesn't support the operation
        # (ie. any platform not running ISC DHCPD)
        pass

    def setNodeForNetworkBoot(
            self, session: Session, dbNode: Node) -> None: \
        # pylint: disable=unused-argument
        # Update node status to "Expired" and boot from network
        dbNode.state = state.NODE_STATE_EXPIRED
        dbNode.bootFrom = 0

        self.deletePuppetNodeCert(dbNode.name)
