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
import sys
import json
import shutil
import tarfile
from typing import Optional
from subprocess import Popen, PIPE
from configparser import ConfigParser
from .make_backup import get_database_config
from tortuga.config.configManager import ConfigManager


class RestoreBackup(object):
    """
    Restore Tortuga.
    """
    def __init__(self) -> None:
        """
        :return: None
        """
        manager: ConfigManager = ConfigManager()

        parsed: ConfigParser = ConfigParser()
        self.config_path = os.path.join(
            manager.getKitConfigBase(),
            'tortuga.ini'
        )
        parsed.read(self.config_path)

        self.config: dict = get_database_config(parsed, manager)

        self.archive_path: str = os.path.abspath(sys.argv[1])

        self.restore_path: str = '/tmp'

        self.restored_path: str = os.path.join(
            self.restore_path,
            'tortuga-backup'
        )

        self.manifest: Optional[dict] = None

    def __call__(self) -> None:
        """
        :return: None
        """
        self.check_archive()
        self.unpack_archive()
        self.load_manifest()
        self.check_database()
        self.restore_database()
        self.restore_config()
        self.cleanup()

    def check_archive(self) -> None:
        """
        :return: None
        """
        if not tarfile.is_tarfile(self.archive_path):
            raise IOError('{} is not an archive'.format(self.archive_path))

        with tarfile.open(self.archive_path, 'r:bz2') as archive:
            if 'tortuga-backup/manifest.json' not in archive.getnames():
                raise IOError('Archive does not contain `manifest.json`')

    def unpack_archive(self) -> None:
        """
        :return None:
        """
        shutil.copy(
            self.archive_path,
            self.restore_path
        )

        with tarfile.open(self.archive_path, 'r:bz2') as archive:
            archive.extractall(self.restore_path)

    def load_manifest(self) -> None:
        """
        :return: None
        """
        with open(os.path.join(self.restored_path, 'manifest.json')) as f:
            self.manifest = json.load(f)

    def check_database(self) -> None:
        """
        :return: None
        """
        if self.config['engine'] != self.manifest['database']['engine']:
            raise RuntimeError(
                'Running database {} does not match the backed up database'
                ' {}'.format(
                    self.config['engine'],
                    self.manifest['database']['engine']
                )
            )

    def _restore_sqlite(self) -> None:
        """
        :return: None
        """
        path: str = os.path.join(
            self.restored_path,
            self.manifest['database']['path']
        )

        shutil.copy(
            path,
            self.config['path']
        )

    def _restore_mysql(self) -> None:
        """
        :return: None
        """
        path: str = os.path.join(
            self.restore_path,
            self.manifest['database']['path']
        )

        with open(path) as dump:
            with Popen(['mysql'], stdin=dump) as proc:
                proc.wait()

    def restore_database(self) -> None:
        """
        :return: None
        """
        database_map: dict = {
            'sqlite': self._restore_sqlite,
            'mysql': self._restore_mysql
        }

        if self.config['engine'] in database_map.keys():
            database_map[self.config['engine']]()
        else:
            raise NotImplementedError('{} is not supported'.format(
                self.config['engine']
            ))

    def restore_config(self) -> None:
        """
        :return: None
        """
        if not self.manifest.get('config'):
            return  # No config to restore.

        shutil.copy(
            os.path.join(
                self.restored_path,
                self.manifest['config']['path']
            )
        )

    def cleanup(self) -> None:
        """
        :return: None
        """
        shutil.rmtree(self.restored_path)


def main() -> None:
    """
    :return: None
    """
    RestoreBackup()()


if __name__ == '__main__':
    main()
