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

from sqlalchemy.orm.session import Session
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.parameter import Parameter


class GlobalParameterDbApi(TortugaDbApi):
    """
    Global Parameter DB API class
    """

    def __init__(self):
        TortugaDbApi.__init__(self)

        self._globalParametersDbHandler = GlobalParametersDbHandler()

    def getParameter(self, session: Session, name):
        """
        Returns the named parameter
        """

        try:
            dbParam = self._globalParametersDbHandler.getParameter(
                session, name)

            return Parameter.getFromDbDict(dbParam.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def getParameterList(self, session: Session):
        """
        Get list of all available parameters from the db.

            Returns:
                [parameter]
            Throws:
                DbError
        """

        try:
            dbParameters = self._globalParametersDbHandler.getParameterList(
                session)

            return self.getTortugaObjectList(Parameter, dbParameters)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise

    def addParameter(self, session: Session, parameter):
        """
        Insert parameter into the db.

            Returns:
                parameterId
            Throws:
                ParameterAlreadyExists
                DbError
        """

        try:
            self._globalParametersDbHandler.addParameter(
                session, parameter)

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise

    def upsertParameter(self, session: Session, parameter):
        try:
            self._globalParametersDbHandler.upsertParameter(
                session, parameter.getName(), parameter.getValue(),
                description=parameter.getDescription())

            session.commit()
        except TortugaException:
            session.rollback()
            raise
        except Exception:
            session.rollback()
            self.getLogger().exception('upsertParameter failed')
            raise

    def deleteParameter(self, session: Session, name):
        """
        Delete parameter from the db.

            Returns:
                None
            Throws:
                ParameterNotFound
                DbError
        """

        try:
            p = self._globalParametersDbHandler.getParameter(session, name)

            self.getLogger().debug('Deleting parameter [%s]' % (name))

            session.delete(p)

            session.commit()

            self.getLogger().info('Deleted parameter [%s]' % name)
        except TortugaException:
            session.rollback()
            raise
        except Exception as ex:
            session.rollback()
            self.getLogger().exception('%s' % ex)
            raise
