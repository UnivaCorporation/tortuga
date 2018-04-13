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

import configparser
from logging import getLogger
import os

import sqlalchemy
import sqlalchemy.orm

from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.dbError import DbError
from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.types import Singleton
from .tables import get_all_table_mappers


logger = getLogger(__name__)


class SessionContextManager(object):
    def __init__(self, dbm):
        self.dbm = dbm
        self.session = None

    def __enter__(self):
        self.session = self.dbm.openSession()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbm.closeSession()


class DbManagerBase(TortugaObjectManager):
    """
    Class for db management.

    :param engine: a SQLAlchemy database engine instance
    :param init:   a flag that is set when the database has not yet
                   been initialized. If this flag is set, not attempts
                   will be made to load/map kit tables. This flag is
                   cleared once the database has been initialized.

    """
    def __init__(self, engine=None):
        super(DbManagerBase, self).__init__()

        self.Session = None

        if not engine:
            self._cm = ConfigManager()

            self._dbConfig = self._refreshDbConfig()

            engineURI = self.__getDbEngineURI()

            if self._dbConfig['engine'] == 'sqlite' and \
                    not os.path.exists(self._dbConfig['path']):
                # Ensure SQLite database file is created with proper permissions
                try:
                    fd = os.open(self._dbConfig['path'],
                                 os.O_CREAT,
                                 mode=0o600)
                finally:
                    os.close(fd)

            if self._dbConfig['engine'] == 'mysql':
                # Set default SQLAlchemy engine arguments for MySQL
                kwargs = {
                    'pool_size': 10,
                    'max_overflow': 2,
                    'pool_recycle': 600,
                    'echo': False,
                    'pool_timeout': 60,
                }
            else:
                kwargs = {}

            self._engine = sqlalchemy.create_engine(engineURI, **kwargs)
        else:
            self._engine = engine

        self._metadata = sqlalchemy.MetaData(self._engine)
        self._mapped_tables = {}

    def _map_db_tables(self):
        #
        # Make sure all kit table mappers have been registered
        #
        load_kits()
        for kit_installer_class in get_all_kit_installers():
            kit_installer = kit_installer_class()
            kit_installer.register_database_table_mappers()
        #
        # Map all tables that haven't yet been mapped
        #
        for table_mapper in get_all_table_mappers():
            key = table_mapper.__name__
            if key not in self._mapped_tables.keys():
                logger.debug('Mapping table: {}'.format(key))
                self._mapped_tables[key] = table_mapper()
                self._mapped_tables[key].map(self)

    @property
    def engine(self):
        """
        SQLAlchemy Engine object property
        """
        self._map_db_tables()
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
        self._map_db_tables()
        try:
            self._metadata.create_all(self.engine)
        except Exception:
            self.getLogger().exception('SQLAlchemy raised exception')
            raise DbError('Check database settings or credentials')

    @property
    def metadata(self):
        return self._metadata

    def __getDbEngineURI(self):
        dbPort = self._dbConfig['port']
        dbHost = self._dbConfig['host']
        engine = self._dbConfig['engine']
        dbUser = self._dbConfig['username']
        dbPassword = self._dbConfig['password']

        if engine == 'sqlite':
            engineURI = 'sqlite:///%s' % (self._dbConfig['path'])
        else:
            if dbUser is not None:
                if dbPassword is not None:
                    userspec = '%s:%s' % (dbUser, dbPassword)
                else:
                    userspec = dbUser
            else:
                userspec = None

            if dbPort is not None:
                hostspec = '%s:%s' % (dbHost, dbPort)
            else:
                hostspec = dbHost

            if userspec is not None:
                engineURI = '%s://%s@%s/%s' % (
                    engine, userspec, hostspec, self._cm.getDbSchema())
            else:
                engineURI = '%s://%s/%s' % (
                    engine, hostspec, self._cm.getDbSchema())

        return engineURI

    def _getDefaultDbEngine(self): \
            # pylint: disable=no-self-use
        return 'sqlite'

    def _getDefaultDbHost(self): \
            # pylint: disable=no-self-use
        return 'localhost'

    def _getDefaultDbPort(self, engine): \
            # pylint: disable=no-self-use
        # MySQL default port
        if engine == 'mysql':
            return 3306

        return None

    def _getDefaultDbUserName(self):
        return self._cm.getDbUser()

    def _getDefaultDbPassword(self):
        if os.path.exists(self._cm.getDbPasswordFile()):
            with open(self._cm.getDbPasswordFile()) as fp:
                dbPassword = fp.read()
        else:
            dbPassword = None

        return dbPassword

    def _refreshDbConfig(self, cfg=None):
        dbConfig = {}

        if cfg is None:
            cfg = configparser.ConfigParser()

            cfg.read(os.path.join(self._cm.getKitConfigBase(), 'tortuga.ini'))

        # Database engine
        val = cfg.get('database', 'engine').strip().lower() \
            if cfg.has_option('database', 'engine') else \
            self._getDefaultDbEngine()

        dbConfig['engine'] = val

        if dbConfig['engine'] == 'sqlite':
            # If database is sqlite, read the path
            dbConfig['path'] = cfg.get('database', 'path') \
                if cfg.has_section('database') and \
                cfg.has_option('database', 'path') else \
                os.path.join(self._cm.getEtcDir(),
                             self._cm.getDbSchema() + '.sqlite')

        # Database host
        val = cfg.get('database', 'host') \
            if cfg.has_option('database', 'host') else \
            self._getDefaultDbHost()

        dbConfig['host'] = val

        # Database port
        val = cfg.get('database', 'port') \
            if cfg.has_option('database', 'port') else None

        dbConfig['port'] = val if val else self._getDefaultDbPort(
            engine=dbConfig['engine'])

        # Database username
        val = cfg.get('database', 'username') \
            if cfg.has_option('database', 'username') \
            else self._getDefaultDbUserName()

        dbConfig['username'] = val

        # Database password
        val = cfg.get('database', 'password') \
            if cfg.has_option('database', 'password') \
            else self._getDefaultDbPassword()

        dbConfig['password'] = val

        return dbConfig

    def get_backend_opts(self): \
            # pylint: disable=no-self-use
        return {
            'mysql_engine': 'InnoDB',
        }

    def getMetadataTable(self, table):
        return self._metadata.tables[table]

    def openSession(self):
        """ Open db session. """
        session_factory = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.Session = sqlalchemy.orm.scoped_session(session_factory)

        return self.Session()

    def closeSession(self):
        """Close scoped_session."""

        self.Session.remove()


class DbManager(DbManagerBase, Singleton):
    pass
