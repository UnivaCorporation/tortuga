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

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.resourceNotFound import ResourceNotFound
from .models.resourceAdapter import ResourceAdapter
from .models.resourceAdapterConfig import ResourceAdapterConfig


class ResourceAdapterConfigDbHandler(TortugaDbObjectHandler):
    """
    Low-level API for managing resource adapter credentials
    
    """
    def get(self, session: Session, resadapter_name: str, name: str) \
            -> ResourceAdapterConfig:
        """
        Returns resource adapter configuration

        Raises:
            ResourceNotFound
            ResourceAdapterNotFound
        """

        self._logger.debug(
            'ResourceAdapterConfigDbHandler.get(resadapter_name=[{}],'
            ' name=[{}]'.format(resadapter_name, name))

        try:
            return session.query(ResourceAdapterConfig).join(
                ResourceAdapter).filter(
                    and_(ResourceAdapter.name == resadapter_name,
                         ResourceAdapterConfig.name == name)).one()
        except NoResultFound:
            raise ResourceNotFound(
                'Resource adapter configuration [{1}] does not exist for'
                ' resource adapter [{0}]'.format(resadapter_name, name))
