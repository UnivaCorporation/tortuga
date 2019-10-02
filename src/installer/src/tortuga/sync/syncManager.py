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

import logging
import os.path
import threading
import time
import json

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.logging import SYNC_NAMESPACE
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility.tortugaSubprocess import TortugaSubprocess
from tortuga.utility import tortugaStatus
from tortuga.utility.runManager import RunManager


class SyncManager(TortugaObjectManager):
    """Class for cluster sync management"""

    __instanceLock = threading.RLock()

    # update delay increase (seconds)
    CLUSTER_UPDATE_DELAY_INCREASE = 30

    # after this limit is reached, warning will be logged
    CLUSTER_UPDATE_WARNING_LIMIT = 10

    def __init__(self):
        super(SyncManager, self).__init__()

        self._isUpdateScheduled = False
        self._isUpdateRunning = False
        self._cm = ConfigManager()
        self._logger = logging.getLogger(SYNC_NAMESPACE)

    def __runClusterUpdate(self, opts={}):
        """ Run cluster update. """
        self._logger.debug('Update timer running, opts={}'.format(opts))

        updateCmd = os.path.join(self._cm.getBinDir(),
                                 'run_cluster_update.sh')

        delay = 0
        updateCnt = 0
        while self.__resetIsUpdateScheduled():
            self._isUpdateRunning = True

            self._logger.debug(
                'New cluster update delay: %s seconds' % (delay))

            time.sleep(delay)
            delay += SyncManager.CLUSTER_UPDATE_DELAY_INCREASE

            # Log warning if timer has been running for too many times.
            updateCnt += 1
            self._logger.debug(
                'Cluster update timer count: %s' % (updateCnt))

            if updateCnt > SyncManager.CLUSTER_UPDATE_WARNING_LIMIT:
                self._logger.warning(
                    'Cluster updated more than %s times using the same'
                    ' timer (possible configuration problem)' % (
                        SyncManager.CLUSTER_UPDATE_WARNING_LIMIT))

            self._logger.debug(
                'Starting cluster update using: %s' % (updateCmd))

            # Since we might sleep for a while, we need to
            # reset update flag just before we run update to avoid
            # unnecessary syncs.

            self.__resetIsUpdateScheduled()

            if 'node' in opts:
                node_update = opts['node']
                env = {**os.environ,
                       'PATH': '/opt/tortuga/bin:' + os.environ['PATH'],
                       'TORTUGA_ROOT': '/opt/tortuga',
                       'FACTER_node_tags_update' : json.dumps(node_update)
                      }
                self._logger.debug('FACTER_node_tags_update={}'.format(env['FACTER_node_tags_update']))
                p = TortugaSubprocess(updateCmd, env=env)
            elif 'software_profile' in opts:
                swp_update = opts['software_profile']
                env = {**os.environ,
                       'PATH': '/opt/tortuga/bin:' + os.environ['PATH'],
                       'TORTUGA_ROOT': '/opt/tortuga',
                       'FACTER_softwareprofile_tags_update' : json.dumps(swp_update)
                      }
                self._logger.debug('FACTER_softwareprofile_tags_update={}'.format(env['FACTER_softwareprofile_tags_update']))
                p = TortugaSubprocess(updateCmd, env=env)
            else:
                p = TortugaSubprocess(updateCmd)

            try:
                p.run()
                self._logger.debug('Cluster update successful')
                self._logger.debug('stdout: {}'.format(p.getStdOut().decode().rstrip()))
                self._logger.debug('stderr: {}'.format(p.getStdErr().decode().rstrip()))
            except CommandFailed:
                if p.getExitStatus() == tortugaStatus.\
                        TORTUGA_ANOTHER_INSTANCE_OWNS_LOCK_ERROR:
                    self._logger.debug(
                        'Another cluster update is already running, will'
                        ' try to reschedule it')

                    self._isUpdateRunning = False

                    self.scheduleClusterUpdate(
                        updateReason='another update already running',
                        delay=60, opts=opts)

                    break
                else:
                    self._logger.error(
                        'Update command "%s" failed (exit status: %s):'
                        ' %s' % (
                            updateCmd, p.getExitStatus(), p.getStdErr()))

            self._logger.debug('Done with cluster update')

        self._isUpdateRunning = False

        self._logger.debug('Update timer exiting')

    def __resetIsUpdateScheduled(self):
        """ Reset cluster update flag, return old flag value. """
        SyncManager.__instanceLock.acquire()
        try:
            flag = self._isUpdateScheduled
            self._isUpdateScheduled = False
            return flag
        finally:
            SyncManager.__instanceLock.release()

    def scheduleClusterUpdate(self, updateReason=None, delay=5, opts={}):
        """ Schedule cluster update. """
        SyncManager.__instanceLock.acquire()
        try:
            if self._isUpdateScheduled:
                # Already scheduled.
                return

            # Start update timer if needed.
            self._isUpdateScheduled = True
            if not self._isUpdateRunning:
                self._logger.debug(
                    'Scheduling cluster update in %s seconds,'
                    ' reason: %s, opts: %s' % (delay, updateReason, opts))

                t = threading.Timer(delay, self.__runClusterUpdate, kwargs=dict(opts=opts))

                t.start()
            else:
                self._logger.debug(
                    'Will not schedule new update timer while the old'
                    ' timer is running')
        finally:
            SyncManager.__instanceLock.release()

    def getUpdateStatus(self):  # pylint: disable=no-self-use
        """ Check cluster update flag. """
        return RunManager().checkLock('cfmsync')
