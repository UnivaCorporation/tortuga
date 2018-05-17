import cherrypy
from sqlalchemy.orm import scoped_session, sessionmaker


class DatabaseTool(cherrypy.Tool):
    def __init__(self):
        super(DatabaseTool, self).__init__(
            'on_start_resource', self.bind_session, priority=20)
        self.session = scoped_session(sessionmaker(autoflush=True,
                                                   autocommit=False))

    def _setup(self):
        super(DatabaseTool, self)._setup()
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)

    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)
        cherrypy.request.db = self.session

    def commit_transaction(self):
        cherrypy.request.db = None

        try:
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

        finally:
            self.session.remove()