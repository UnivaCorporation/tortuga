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
import logging
from typing import List, Optional

from sqlalchemy.orm.session import Session
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.kit.manager import KitManager
from tortuga.logging import KIT_NAMESPACE
from tortuga.objects.kit import Kit
from tortuga.utility.tortugaApi import TortugaApi

from .eula import CommandLineEulaValidator


class KitApi(TortugaApi):
    """
    Kit API class.
    """
    def __init__(self):
        super().__init__()
        
        self._kit_manager = KitManager(
            eula_validator=CommandLineEulaValidator()
        )
        self._logger = logging.getLogger(KIT_NAMESPACE)

    def getKit(self, session: Session, name: str,
               version: Optional[str] = None,
               iteration: Optional[str] = None) -> Kit:
        """
        Get kit info.

            Returns:
                kit
            Throws:
                KitNotFound
                TortugaException
        """
        try:
            return self._kit_manager.getKit(
                session, name, version=version, iteration=iteration)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getKitById(self, session: Session, id_):
        """
        Get kit info by kitId.

            Returns:
                kit
            Throws:
                KitNotFound
                TortugaException
        """
        try:
            return self._kit_manager.getKitById(session, id_)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))

    def getKitList(self, session: Session):
        """
        Get kit list.

            Returns:
                [kits]
            Throws:
                TortugaException
        """
        try:
            kitList = self._kit_manager.getKitList(session)
            return kitList

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def installKit(self, session: Session, name, version, iteration=None):
        """
        Install kit using kit name/version/iteration.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """
        try:
            return self._kit_manager.installKit(
                session, name, version, iteration)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def installKitPackage(self, db_manager, packageUrl):
        """
            Install kit package.

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """
        try:
            return self._kit_manager.installKitPackage(db_manager, packageUrl)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getKitEula(self, name, version, iteration=None):
        """
            Fetch eula information for kit.

            Returns:
                eula tortuga object
            Throws:
                UserNotAuthorized
                FileNotFound
                NoKitEula
                TortugaException
        """
        try:
            return self._kit_manager.get_kit_eula(
                name, version, iteration)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def getKitPackageEula(self, packageUrl):
        """
            Fetch eula information for kit package.

            Returns:
                eula tortuga object
            Throws:
                UserNotAuthorized
                FileNotFound
                NoKitEula
                TortugaException
        """
        try:
            return self._kit_manager.get_kit_package_eula(packageUrl)

        except TortugaException:
            raise

        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)

    def installOsKit(self, session: Session, os_media_urls: List[str],
                     **kwargs) -> Kit:
        """
            Install OS kit

            Returns:
                kitId
            Throws:
                UserNotAuthorized
                FileNotFound
                KitAlreadyExists
                TortugaException
        """
        try:
            return self._kit_manager.installOsKit(
                session, os_media_urls, **kwargs)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(ex)
            raise TortugaException(exception=ex)

    def deleteKit(self, name, version=None, iteration=None, force=False) -> None:
        """
        Delete kit.

            Returns:
                None
            Throws:
                UserNotAuthorized
                KitNotFound
                KitInUse
                TortugaException
        """
        try:
            self._kit_manager.deleteKit(
                name, version, iteration, force=force)
        except TortugaException:
            raise
        except Exception as ex:
            self._logger.exception(str(ex))
            raise TortugaException(exception=ex)
