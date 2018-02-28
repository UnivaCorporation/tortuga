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

import mock
import unittest
from . import Puppet


class PuppetTest(unittest.TestCase):
    """
    Test case for Puppet.
    """
    def setUp(self):
        """
        :return: None
        """
        self.puppet = Puppet()

    @mock.patch('puppet.Popen')
    def testAgent(self, mock_popen):
        """
        :return: None
        """
        expected_args = [
            '--no-daemonize',
            '--verbose',
            '--onetime'
        ]

        mock_popen.return_value.returncode = 0
        mock_popen.return_value.communicate.return_value = ('Running Puppet', '')

        self.puppet.agent(
            daemonize=False,
            verbose=True,
            one_time=True
        )

        self.assertEqual(
            expected_args,
            mock_popen.call_args_list
        )
