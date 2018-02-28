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

# pylint: disable=no-self-use

import os
import logging
from tortuga.exceptions.abstractMethod import AbstractMethod


class ActionsBase(object):
    """Base class for holding common configuration logic"""

    def __init__(self):
        self._configParser = None
        self._logger = logging.getLogger(
            'tortuga.kit.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

    def getConfigDefaults(self):
        return {}

    def getConfigFile(self):
        raise AbstractMethod("The getConfigFile method must be overriden"
                             " in the derived class")

    def writeDefaultConfig(self):
        import configparser
        # Make sure we start with an empty config parser
        configParser = configparser.ConfigParser()
        self.setDefaults(configParser)
        self.writeConfig()

    def getConfig(self, reread=False):
        if self._configParser is None or reread:
            configFile = self.getConfigFile()
            if configFile is not None:
                import configparser
                try:
                    self._configParser = configparser.ConfigParser()
                    self._configParser.read(configFile)
                except Exception:
                    self._logger.\
                        debug('no valid configuration for component: %s')
        return self._configParser

    def setDefaults(self, configParser=None):
        import configparser
        if configParser is None:
            configParser = self.getConfig()
        values = self.getConfigDefaults()
        defConfigParser = configparser.ConfigParser()
        if values is not None:
            for k, v in list(values.items()):
                if not defConfigParser.has_section(k):
                    defConfigParser.add_section(k)
                if v is not None:
                    for vk, vv in list(v.items()):
                        defConfigParser.set(k, vk, vv)

        # Now override program defaults with existing values
        for section in configParser.sections():
            if not defConfigParser.has_section(section):
                defConfigParser.add_section(section)
            for option in configParser.options(section):
                defConfigParser.set(
                    section, option, configParser.get(section, option))

        # Finally set the internal config parser to our new defaults
        self._configParser = defConfigParser

    def writeConfig(self):
        configFile = self.getConfigFile()
        if configFile is not None:
            if not os.path.exists(os.path.dirname(configFile)):
                os.makedirs(os.path.dirname(configFile))
            # Write the current config parser
            configParser = self.getConfig()
            fd = open(configFile, 'w')
            try:
                configParser.write(fd)
            finally:
                fd.close()
