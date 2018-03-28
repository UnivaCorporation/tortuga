class SessionContextManager(object):
    def __init__(self, dbm):
        self.dbm = dbm
        self.session = None

    def __enter__(self):
        self.session = self.dbm.openSession()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbm.closeSession()
