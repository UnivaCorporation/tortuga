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
import tempfile


class BaseEulaValidator:
    """
    This is the base class for EULA validators. A EULA validator is
    responsible for displaying the EULA to the person installing the kit
    and validating whether or not the user accepts it. The default behavior
    for this validator is to return False (i.e. the user does not accept
    the EULA) if the installer has a EULA, otherwise return True.

    """
    def validate_eula(self, eula=None, auto_accept=False):
        """
        Displays the EULA to the person installing the kit and asks them
        to accept it.

        :param eula:        an instance of Eula
        :param auto_accept: whether or not to auto accept the EULA
        :return:            True if the user accepts the Eula, False otherwise

        """
        if not eula or auto_accept:
            return True
        return False


class CommandLineEulaValidator(BaseEulaValidator):
    """
    An implementation of the BaseEulaValidator that displays and validates
    the EULA on the commandline

    """
    def __init__(self):
        super().__init__()
        self._eula_file = None

    def validate_eula(self, eula=None, auto_accept=False):
        if not eula:
            return True

        self._eula_file = tempfile.NamedTemporaryFile()
        try:
            self._eula_file.write(eula.text.encode())
            self._eula_file.flush()
            if auto_accept:
                result = self._auto_accept_eula()
            else:
                result = self._accept_eula()
        finally:
            self._eula_file.close()
        return result

    def _auto_accept_eula(self):
        cmd = 'fold -s {}'.format(self._eula_file.name)
        os.system(cmd)
        return True

    def _accept_eula(self):
        print('To install this kit you must read and agree to the '
              'following EULA.')
        print("Press 'Enter' to continue...")
        input('')

        cmd = 'fold -s {} | more'.format(self._eula_file.name)
        os.system(cmd)
        print()

        while True:
            print('Do you agree? [Yes / No]', end=' ')
            answer = input('').lower()
            if answer not in ['yes', 'no', 'y', 'n']:
                print ("Invalid response. Please respond 'Yes' or 'No'")
            else:
                break

        if answer[0] == 'n':
            return False
        return True
