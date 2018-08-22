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

import subprocess

from tortuga.exceptions.commandFailed import CommandFailed


class TortugaSubprocess(subprocess.Popen):
    def __init__(self, args, bufsize=0, executable=None, stdin=None,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                 preexec_fn=None, close_fds=False, shell=True, cwd=None,
                 env=None, universal_newlines=False, startupinfo=None,
                 creationflags=0, useExceptions=True): \
            # pylint: disable=too-many-locals
        """
        Overrides Popen constructor with defaults more appropriate for
        Tortuga usage.
        """

        subprocess.Popen.__init__(
            self, args, bufsize, executable, stdin, stdout, stderr,
            preexec_fn, close_fds, shell, cwd, env, universal_newlines,
            startupinfo, creationflags)

        self._stdout = None
        self._stderr = None
        self._args = args
        self._useExceptions = useExceptions

    def run(self, input_=None):
        """ Run subprocess. """

        self._stdout, self._stderr = subprocess.Popen.communicate(
            self, input_)

        if self.returncode != 0 and self._useExceptions:
            raise CommandFailed('%s' % (self._stderr.rstrip()))

        return self._stdout, self._stderr

    def getArgs(self):
        return self._args

    def getStdOut(self):
        return self._stdout

    def getStdErr(self):
        return self._stderr

    def getExitStatus(self):
        return self.returncode


# Convenience function for executing command.
def executeCommand(command):
    """ Create subprocess and run it, return subprocess object. """

    p = TortugaSubprocess(command)

    p.run()

    return p


# Convenience function for executing command that may fail, and we do not
# care about the failure.
def executeCommandAndIgnoreFailure(command):
    """
    Create subprocess, run it, ignore any failures, and return
    subprocess object.
    """

    p = TortugaSubprocess(command)

    try:
        p.run()
    except CommandFailed:
        pass

    return p
