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

from cherrypy.process import plugins

from tortuga.web_service import dbm


class DatabasePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        super(DatabasePlugin, self).__init__(bus)
        self.sa_engine = None
        self.bus.subscribe('bind', self.bind)

    def start(self):
        self.sa_engine = dbm.engine

    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self, session):
        session.configure(bind=self.sa_engine)
