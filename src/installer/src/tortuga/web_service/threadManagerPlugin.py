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

import threading
from cherrypy.process import plugins
from .threadManager import threadManager
from .worker import worker_thread
from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers


class ThreadManagerPlugin(plugins.SimplePlugin):
    def start(self):
        self.bus.log(
            '[{0}] Initializing thread manager'.format(
                self.__class__.__name__))

        #
        # Ensure that all kit worker actions are loaded
        #
        load_kits()
        for kit_installer_class in get_all_kit_installers():
            kit_installer = kit_installer_class()
            kit_installer.register_web_service_worker_actions()

        # Create 8 worker threads
        num_worker_threads = 8

        self.bus.log(
            '[{0}] Initializing {1} worker threads'.format(
                self.__class__.__name__, num_worker_threads))

        for thread_id in range(num_worker_threads):
            t = threading.Thread(target=worker_thread,
                                 args=(thread_id, threadManager))
            t.setDaemon(True)
            t.start()

    start.priority = 85
