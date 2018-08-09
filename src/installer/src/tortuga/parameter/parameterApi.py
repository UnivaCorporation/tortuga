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

from typing import Optional

from sqlalchemy.orm.session import Session
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.parameter import Parameter
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.parameter.parameterManager import ParameterManager
from tortuga.utility.tortugaApi import TortugaApi


class ParameterApi(TortugaApi):
    """
    Parameter API class.
    """

    def getParameter(self, session: Session, name: str) -> Parameter:
        """
        Get parameter.

            Returns:
                parameter
            Throws:
                ParameterNotFound
                TortugaException
        """

        try:
            return ParameterManager().getParameter(session, name)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getBoolParameter(self, session: Session, name: str,
                         default: Optional[bool] = None) -> bool:
        """
        Get bool parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            return ParameterManager().getBoolParameter(
                session, name, default)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getIntParameter(self, session: Session, name: str,
                        default: Optional[int] = None) -> int:
        """
        Get int parameter.

        Raises:
            ParameterNotFound
            TortugaException
        """

        try:
            return ParameterManager().getIntParameter(
                session, name, default)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))

            raise TortugaException(exception=ex)

    def getParameterList(self, session: Session) -> TortugaObjectList:
        """
        Get all known parameters.

            Returns:
                [parameter]
            Throws:
                TortugaException
        """

        try:
            return ParameterManager().getParameterList(session)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise TortugaException(exception=ex)

    def upsertParameter(self, session: Session, parameter: Parameter) \
            -> None:
        try:
            return ParameterManager().upsertParameter(session, parameter)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error upserting parameter [%s]' % (parameter.getName()))

            raise TortugaException(exception=ex)

    def deleteParameter(self, session: Session, name: str) -> None:
        """
        Delete parameter by name
        """

        try:
            ParameterManager().deleteParameter(session, name)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(
                'Error deleting parameter [%s]' % (name))

            raise TortugaException(exception=ex)
