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
