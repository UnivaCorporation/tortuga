#!/usr/bin/env python

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
import os
import json
import shutil
import tarfile
from time import time
from configparser import ConfigParser
from tortuga.config.configManager import ConfigManager


def get_database_config(parsed: ConfigParser, manager: ConfigManager) -> dict:
    """
    Generate a populated
    configuration dictionary.
    TODO: This should be shared
    with dbManager.py.

    :param parsed: ConfigParser
    :param manager: ConfigManager
    :return: Dictionary
    """
    config: dict = {}

    config['engine'] = parsed.get('database', 'engine') if \
        parsed.has_option('database', 'engine') else \
        'sqlite'

    config['host'] = parsed.get('database', 'host') if \
        parsed.has_option('database', 'host') else \
        'localhost'

    config['username'] = parsed.get('database', 'username') if \
        parsed.has_option('database', 'username') else \
        manager.getDbUser()

    config['password'] = parsed.get('database', 'password') if \
        parsed.has_option('database', 'password') else \
        manager.getDbPassword()

    if config['engine'] == 'sqlite':
        config['port'] = None
        config['path'] = parsed.get('database', 'path') if \
            parsed.has_option('database', 'path') else \
            os.path.join(
                manager.getEtcDir(),
                manager.getDbSchema() + '.sqlite'
            )
    elif config['engine'] == 'mysql':
        config['path'] = None
        config['port'] = manager.get('database', 'port') if \
            manager.has_option('database', 'port') else \
            3306
    else:
        raise NotImplementedError('{} is not supported'.format(
            config['engine']
        ))

    return config


class MakeBackup(object):
    """
    Backup Tortuga.
    """
    def __init__(self) -> None:
        """
        :return: None
        """
        timestamp: int = int(time())
        backup_directory: str = 'tortuga-backup-{}'.format(timestamp)
        self.backup_path: str = os.path.join('/tmp', backup_directory)
        self.backup_archive: str = self.backup_path + '.tar.bz2'

        manager: ConfigManager = ConfigManager()

        parsed: ConfigParser = ConfigParser()
        self.config_path = os.path.join(
            manager.getKitConfigBase(),
            'tortuga.ini'
        )
        parsed.read(self.config_path)

        self.config: dict = get_database_config(parsed, manager)

        self.manifest: dict = {}

    def __call__(self) -> None:
        """
        :return: None
        """
        os.mkdir(self.backup_path)
        self.backup_database()
        self.backup_config()
        self.write_manifest()
        self.make_archive()
        shutil.rmtree(self.backup_path)
        shutil.move(
            self.backup_archive,
            os.getcwd()
        )

    def _backup_sqlite(self) -> None:
        """
        :return: None
        """
        self.manifest['database']['path']: str = \
            os.path.basename(self.config['path'])

        shutil.copy(
            self.config['path'],
            os.path.join(
                self.backup_path,
                os.path.basename(self.config['path'])
            )
        )

    def _backup_mysql(self) -> None:
        """
        :return: None
        """
        pass

    def backup_database(self) -> None:
        """
        :return: None
        """
        database_map: dict = {
            'sqlite': self._backup_sqlite,
            'mysql': self._backup_mysql
        }

        self.manifest['database']: dict = {}

        self.manifest['database']['engine']: str = \
            self.config['engine']

        if self.config['engine'] in database_map.keys():
            database_map[self.config['engine']]()
        else:
            raise NotImplementedError('{} is not supported'.format(
                self.config['engine']
            ))

    def backup_config(self) -> None:
        """
        :return: None
        """
        if os.path.isfile(self.config_path):

            self.manifest['config']: dict = {}
            self.manifest['config']['path']: str = \
                os.path.basename(self.config_path)

            shutil.copy(
                self.config_path,
                self.backup_path
            )

    def write_manifest(self) -> None:
        """
        :return: None
        """
        manifest_path: str = os.path.join(
            self.backup_path,
            'manifest.json'
        )

        with open(manifest_path, 'w') as out:
            json.dump(self.manifest, out)

    def make_archive(self) -> None:
        """
        :return: None
        """
        with tarfile.open(self.backup_archive, 'w:bz2') as out:
            out.add(self.backup_path, arcname='tortuga-backup')


def main() -> None:
    """
    :return: None
    """
    MakeBackup()()


if __name__ == '__main__':
    main()
