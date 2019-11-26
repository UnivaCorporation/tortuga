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

# pylint: disable=multiple-statements,no-member,no-name-in-module
# pylint: disable=not-callable

import os

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
import sqlalchemy.orm

from tortuga.config.configManager import ConfigManager
from tortuga.kit.registry import get_all_kit_installers
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from .models.base import ModelBase
from .sessionContextManager import SessionContextManager


@compiles(sqlalchemy.String, 'sqlite')
def compile_unicode(element, compiler, **kw):
    element.collation = None
    return compiler.visit_string(element, **kw)


class DbManager(TortugaObjectManager):
    """
    Class for db management.

    :param engine: a SQLAlchemy database engine instance
    :param init:   a flag that is set when the database has not yet
                   been initialized. If this flag is set, not attempts
                   will be made to load/map kit tables. This flag is
                   cleared once the database has been initialized.

    """
    def __init__(self, engine=None):
        super().__init__()

        if not engine:
            self._cm = ConfigManager()
            engine = self._cm.getDbEngine()
            schema = self._cm.getDbSchema()

            engineURI = self.__getDbEngineURI()

            if engine == 'sqlite' and not os.path.exists(schema):
                # Ensure SQLite database file is created with proper
                # permissions
                fd = os.open(schema, os.O_CREAT, mode=0o600)
                os.close(fd)

            self._engine = sqlalchemy.create_engine(engineURI, pool_pre_ping=True)

        else:
            self._engine = engine

        self.Session = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine))

    def _register_database_tables(self):
        for kit_installer_class in get_all_kit_installers():
            kit_installer = kit_installer_class()
            kit_installer.register_database_tables()

    @property
    def engine(self):
        """
        SQLAlchemy Engine object property
        """
        self._register_database_tables()
        return self._engine

    def session(self):
        """
        Database session context manager
        """
        return SessionContextManager(self)

    def init_database(self):
        #
        # Create tables
        #
        self._register_database_tables()
        ModelBase.metadata.create_all(self.engine)

    @property
    def metadata(self):
        return self._metadata

    def __getDbEngineURI(self):
        engine = self._cm.getDbEngine()
        schema = self._cm.getDbSchema()
        driver = ''
        host = ''
        port = ''
        user = ''
        password = ''

        if engine == 'mysql':
            driver = "+pymysql"
            host = self._cm.getDbHost()
            port = self._cm.getDbPort()
            user = self._cm.getDbUser()
            password = self._cm.getDbPassword()

        userspec = ''
        if user:
            if password:
                userspec = '{}:{}@'.format(user, password)
            else:
                userspec = '{}@'.format(user)

        hostspec = ''
        if host:
            if port:
                hostspec = '{}:{}'.format(host, port)
        else:
            hostspec = host

        engineURI = "{}{}://{}{}/{}".format(engine, driver, userspec,
                                            hostspec, schema)

        return engineURI

    def getMetadataTable(self, table):
        return self._metadata.tables[table]

    def openSession(self):
        """ Open db session. """

        return self.Session()

    def closeSession(self):
        """Close scoped_session."""

        self.Session.remove()
