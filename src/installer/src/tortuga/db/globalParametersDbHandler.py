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

# pylint: disable=not-callable,multiple-statements,no-member

from typing import NoReturn, List
from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.globalParameters import GlobalParameters
from tortuga.exceptions.parameterAlreadyExists import ParameterAlreadyExists
from tortuga.exceptions.parameterNotFound import ParameterNotFound


class GlobalParametersDbHandler(TortugaDbObjectHandler):
    """
    This class handles global parameters table.
    """

    def getParameter(self, session, name: str) -> GlobalParameters:
        """
        Return parameter.

        Raises:
            ParameterNotFound
        """

        self.getLogger().debug('Retrieving parameter [%s]' % (name))

        try:
            return session.query(GlobalParameters).filter(
                GlobalParameters.name == name).one()
        except NoResultFound:
            raise ParameterNotFound('Parameter [%s] not found.' % (name))

    def getParameterList(self, session) -> List[GlobalParameters]:
        """
        Get list of parameters from the db.
        """

        self.getLogger().debug('Retrieving parameter list')

        return session.query(GlobalParameters).all()

    def addParameter(self, session, parameter) -> GlobalParameters:
        """
        Insert parameter into the db.

        Raises:
            ParameterAlreadyExists
        """

        self.getLogger().debug(
            'Inserting parameter [%s]' % (parameter.getName()))

        try:
            self.getParameter(session, parameter.getName())

            raise ParameterAlreadyExists(
                'Parameter [%s] already exists' % (parameter))
        except ParameterNotFound:
            # OK.
            pass

        dbParameter = GlobalParameters(
            name=parameter.getName(),
            value=parameter.getValue(),
            description=parameter.getDescription())

        session.add(dbParameter)

        return dbParameter

    def upsertParameter(self, session, name: str, value: str,
                        description=None) -> GlobalParameters:
        try:
            dbParameter = self.getParameter(session, name)
        except ParameterNotFound:
            dbParameter = GlobalParameters()

            session.add(dbParameter)

        dbParameter.name = name
        dbParameter.value = value

        if description is not None:
            dbParameter.description = description
        elif not description:
            dbParameter.description = None

        return dbParameter

    def deleteParameter(self, session, name: str) -> NoReturn:
        """
        Delete parameter from the db.

        Raises:
            ParameterNotFound
        """

        self.getLogger().debug('Deleting parameter [%s]' % (name))

        dbParameter = self.getParameter(session, name)

        session.delete(dbParameter)

        self.getLogger().info('Deleted parameter [%s]' % name)
