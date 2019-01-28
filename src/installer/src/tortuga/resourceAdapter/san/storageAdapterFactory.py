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
from tortuga.config.configManager import ConfigManager
from tortuga.logging import STORAGE_ADAPTER_NAMESPACE


def get_api(moduleName):
    logger = logging.getLogger(STORAGE_ADAPTER_NAMESPACE)

    # Add the module's directory to PYTHONPATH
    cm = ConfigManager()
    moduleDir = '%s/lib/tortuga/resourceAdapter/san' % cm.getRoot()
    import sys
    sys.path.insert(0, moduleDir)

    # Import the module
    try:
        mod = __import__(moduleName)
    except Exception as msg:
        logger.error("Can't import module [%s]; %s" % (moduleName, msg))
        raise

    # Create the class
    className = moduleName[0].upper() + moduleName[1:]

    try:
        klass = getattr(mod, className)
    except Exception as msg:
        logger.error(
            "Can't create class [%s] from module [%s]; %s" % (
                className, moduleName, msg))

        raise

    # Instantiate an object of the class
    try:
        obj = klass()
    except Exception as msg:
        logger.error(
            "Can't create object of class [%s] from module [%s]; %s" % (
                className, moduleName, msg))

        raise

    # Undo changes to PYTHONPATH.
    del sys.path[0]

    return obj
