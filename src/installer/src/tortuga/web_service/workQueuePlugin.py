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
from cherrypy.process import plugins
import zmq
from tortuga.types import Singleton
from . import app


class Workqueue(Singleton):
    def __init__(self):
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PUB)

        sockfn = os.path.join(app.cm.getRoot(), 'var/tmp/tortugawsd.sock')

        self.__socket.bind('ipc://%s' % (sockfn))

    @property
    def socket(self):
        return self.__socket

    @property
    def context(self):
        return self.__context


class WorkQueuePlugin(plugins.SimplePlugin):
    def start(self):
        self.bus.log('WorkQueuePlugin start() called')

        Workqueue()

    start.priority = 80

    def stop(self):
        self.bus.log('WorkQueuePlugin stop() called')

        wq = Workqueue()
        wq.socket.close()
        wq.context.term()
