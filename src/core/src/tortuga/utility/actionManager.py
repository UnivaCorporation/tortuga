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

import base64
import time
import uuid

from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.config.configManager import ConfigManager
from tortuga.types import Singleton


class ActionManager(TortugaObjectManager, Singleton):
    def __init__(self):
        super(ActionManager, self).__init__()

        self._actionBase = "%s%s" % (
            ConfigManager().getRoot(),
            ConfigManager().getActionLog())

    def logAction(self, actionString):
        name = str(uuid.uuid1())
        fullName = '%s/%s' % (self._actionBase, name)
        t = '%015.2f' % time.time()
        line = t + ': ' + actionString + '\n'

        with open(fullName, 'w') as f:
            f.write(str(base64.b64encode(line.encode('utf-8')), 'utf-8'))
