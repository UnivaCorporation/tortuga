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
import threading
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.anotherInstanceOwnsLock \
    import AnotherInstanceOwnsLock
from tortuga.types import Singleton


class RunManager(TortugaObjectManager, Singleton):
    def __init__(self):
        super(RunManager, self).__init__()

        self._lock = threading.RLock()

    def getLockFileName(self, utilityName): \
            # pylint: disable=no-self-use
        if not utilityName:
            raise InvalidArgument('Invalid utility name provided.')
        fsMan = osUtility.getOsObjectFactory().getOsFileSystemManager()
        return '%s/%s' % (fsMan.getOsLockFilePath(), utilityName)

    def getLockFileAndPid(self, utilityName):
        lockFile = self.getLockFileName(utilityName)

        if os.path.exists(lockFile):
            f = open(lockFile, 'r')
            try:
                return lockFile, int(f.read())
            finally:
                f.close()

        return lockFile, None

    def acquireLock(self, utilityName):
        """ Acquire lock file for the given utility. """
        self._lock.acquire()
        try:
            lockFile, pid = self.getLockFileAndPid(utilityName)
            if pid is not None:
                raise AnotherInstanceOwnsLock(
                    'Another instance of %s owns lock file (PID: %s).'
                    % (utilityName, pid))
            else:
                pid = os.getpid()
                open(lockFile, 'w').write('%s' % pid)
                self.getLogger().debug(
                    'Acquired lock file %s for %s' % (
                        lockFile, utilityName))

                return lockFile
        finally:
            self._lock.release()

    def releaseLock(self, utilityName):
        """ Release lock file for the given utility. """
        self._lock.acquire()
        try:
            lockFile, pid = self.getLockFileAndPid(utilityName)
            myPid = '%s' % os.getpid()
            if os.path.exists(lockFile):
                if int(myPid.strip()) != pid:
                    raise AnotherInstanceOwnsLock(
                        'Another instance of %s owns lock file (PID: %s).'
                        % (utilityName, pid))
                else:
                    os.remove(lockFile)
                    self.getLogger().debug(
                        'Released lock file %s for %s'
                        % (lockFile, utilityName))
            else:
                self.getLogger().error(
                    'Ignoring attempt to release unacquired lock file'
                    ' for %s' % (utilityName))
        finally:
            self._lock.release()

    def clearLock(self, utilityName):
        """ Clear lock file for the given utility. """
        self._lock.acquire()
        try:
            lockFile = self.getLockFileName(utilityName)
            if os.path.exists(lockFile):
                os.remove(lockFile)
                self.getLogger().debug(
                    'Cleared lock file %s for %s' % (lockFile, utilityName))
            else:
                self.getLogger().debug(
                    'Lock file %s does not exist for %s'
                    % (lockFile, utilityName))
        finally:
            self._lock.release()

    def checkLock(self, utilityName):
        """ Check if the lockfile exists """
        return self.checkLockPid(utilityName, False)

    def checkLockPid(self, utilityName, checkPid=True):
        """
        Check if the pid that created the lock for utilityName is running
        """

        self._lock.acquire()
        try:
            lockFile, pid = self.getLockFileAndPid(utilityName)
            self.getLogger().debug(
                'checking if %s exists and %s is running' % (lockFile, pid))

            if not os.path.exists(lockFile):
                # if the lock files doesn't exist it isn't running
                return False

            if checkPid:
                try:
                    os.kill(pid, 0)
                except OSError:
                    return False

            return True
        finally:
            self._lock.release()

    def clearLockIfPidNotRunning(self, utilityName):
        """ Clear lock if pid is not running """
        if not self.checkLockPid(utilityName):
            self.clearLock(utilityName)
        else:
            _, pid = self.getLockFileAndPid(utilityName)
            self.getLogger().debug(
                'Not clearing lock for %s as locking pid %d is still active.'
                % (utilityName, pid))
