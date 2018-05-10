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

from typing import List, NoReturn

from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.parameterAlreadyExists import ParameterAlreadyExists
from tortuga.exceptions.parameterNotFound import ParameterNotFound

from .models.globalParameter import GlobalParameter


class GlobalParametersDbHandler(TortugaDbObjectHandler):
    """
    This class handles global parameters table.
    """

    def getParameter(self, session, name: str) -> GlobalParameter:
        """
        Return parameter.

        Raises:
            ParameterNotFound
        """

        self.getLogger().debug('Retrieving parameter [%s]' % (name))

        try:
            return session.query(GlobalParameter).filter(
                GlobalParameter.name == name).one()
        except NoResultFound:
            raise ParameterNotFound('Parameter [%s] not found.' % (name))

    def getParameterList(self, session) -> List[GlobalParameter]:
        """
        Get list of parameters from the db.
        """

        self.getLogger().debug('Retrieving parameter list')

        return session.query(GlobalParameter).all()

    def addParameter(self, session, parameter) -> GlobalParameter:
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

        dbParameter = GlobalParameter(
            name=parameter.getName(),
            value=parameter.getValue(),
            description=parameter.getDescription())

        session.add(dbParameter)

        return dbParameter

    def upsertParameter(self, session, name: str, value: str,
                        description=None) -> GlobalParameter:
        try:
            dbParameter = self.getParameter(session, name)
        except ParameterNotFound:
            dbParameter = GlobalParameter()

            session.add(dbParameter)

        dbParameter.name = name
        dbParameter.value = value

        if description is not None:
            dbParameter.description = description
        elif not description:
            dbParameter.description = None

        return dbParameter
