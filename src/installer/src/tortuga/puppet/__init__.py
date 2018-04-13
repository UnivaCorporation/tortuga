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

from os import devnull
from subprocess import Popen, STDOUT


class Puppet(object):
    """
    Object to drive Puppet.
    """
    def __init__(self, log_file_handle=None):
        """
        :param log_file_handle: File handle
        :return: Puppet instance
        """
        self._path = '/opt/puppetlabs/bin/puppet'
        self._log_file_handle = log_file_handle

    def __exec__(self, argument_list):
        """
        Execute a puppet command.

        :param argument_list: List arguments to execute
        :return: None
        """
        exec_command = [self._path] + argument_list

        if self._log_file_handle:
            out = self._log_file_handle
        else:
            out = open(devnull, 'w')

        process = Popen(
            exec_command,
            stdout=out,
            stderr=STDOUT
        )
        process.communicate()
        process.wait()

        if not self._log_file_handle:
            out.close()

    def agent(self, daemonize=True, verbose=True, one_time=True,
              no_splay=True):
        """
        Execute an agent command.

        :param daemonize: Boolean
        :param verbose: Boolean
        :param one_time: Boolean
        :param no_splay: Boolean
        :return: None
        """
        argument_list = ['agent']

        if daemonize:
            argument_list.append('--daemonize')
        else:
            argument_list.append('--no-daemonize')

        if verbose:
            argument_list.append('--verbose')

        if one_time:
            argument_list.append('--onetime')

        if no_splay:
            argument_list.append('--no-splay')

        self.__exec__(argument_list)
