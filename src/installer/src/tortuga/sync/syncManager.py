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

import os.path
import threading
import time

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.commandFailed import CommandFailed
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

    def __runClusterUpdate(self):
        """ Run cluster update. """
        self.getLogger().debug('Update timer running')

        updateCmd = os.path.join(self._cm.getBinDir(),
                                 'run_cluster_update.sh')

        delay = 0
        updateCnt = 0
        while self.__resetIsUpdateScheduled():
            self._isUpdateRunning = True

            self.getLogger().debug(
                'New cluster update delay: %s seconds' % (delay))

            time.sleep(delay)
            delay += SyncManager.CLUSTER_UPDATE_DELAY_INCREASE

            # Log warning if timer has been running for too many times.
            updateCnt += 1
            self.getLogger().debug(
                'Cluster update timer count: %s' % (updateCnt))

            if updateCnt > SyncManager.CLUSTER_UPDATE_WARNING_LIMIT:
                self.getLogger().warning(
                    'Cluster updated more than %s times using the same'
                    ' timer (possible configuration problem)' % (
                        SyncManager.CLUSTER_UPDATE_WARNING_LIMIT))

            self.getLogger().debug(
                'Starting cluster update using: %s' % (updateCmd))

            # Since we might sleep for a while, we need to
            # reset update flag just before we run update to avoid
            # unnecessary syncs.

            self.__resetIsUpdateScheduled()

            p = TortugaSubprocess(updateCmd)

            try:
                p.run()

                self.getLogger().debug('Cluster update successful')
            except CommandFailed:
                if p.getExitStatus() == tortugaStatus.\
                        TORTUGA_ANOTHER_INSTANCE_OWNS_LOCK_ERROR:
                    self.getLogger().debug(
                        'Another cluster update is already running, will'
                        ' try to reschedule it')

                    self._isUpdateRunning = False

                    self.scheduleClusterUpdate(
                        updateReason='another update already running',
                        delay=60)

                    break
                else:
                    self.getLogger().error(
                        'Update command "%s" failed (exit status: %s):'
                        ' %s' % (
                            updateCmd, p.getExitStatus(), p.getStdErr()))

            self.getLogger().debug('Done with cluster update')

        self._isUpdateRunning = False

        self.getLogger().debug('Update timer exiting')

    def __resetIsUpdateScheduled(self):
        """ Reset cluster update flag, return old flag value. """
        SyncManager.__instanceLock.acquire()
        try:
            flag = self._isUpdateScheduled
            self._isUpdateScheduled = False
            return flag
        finally:
            SyncManager.__instanceLock.release()

    def scheduleClusterUpdate(self, updateReason=None, delay=5):
        """ Schedule cluster update. """
        SyncManager.__instanceLock.acquire()
        try:
            if self._isUpdateScheduled:
                # Already scheduled.
                return

            # Start update timer if needed.
            self._isUpdateScheduled = True
            if not self._isUpdateRunning:
                self.getLogger().debug(
                    'Scheduling cluster update in %s seconds,'
                    ' reason: %s' % (delay, updateReason))

                t = threading.Timer(delay, self.__runClusterUpdate)

                t.start()
            else:
                self.getLogger().debug(
                    'Will not schedule new update timer while the old'
                    ' timer is running')
        finally:
            SyncManager.__instanceLock.release()

    def getUpdateStatus(self):  # pylint: disable=no-self-use
        """ Check cluster update flag. """
        return RunManager().checkLock('cfmsync')
