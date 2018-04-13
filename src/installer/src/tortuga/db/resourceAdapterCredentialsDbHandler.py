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

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists
from tortuga.exceptions.resourceNotFound import ResourceNotFound

from .models.resourceAdapterCredential import ResourceAdapterCredential
from .models.resourceAdapter import ResourceAdapter
from .resourceAdaptersDbHandler import ResourceAdaptersDbHandler


class ResourceAdapterCredentialsDbHandler(TortugaDbObjectHandler):
    """Low-level API for managing resource adapter credentials"""

    def __raise_not_found_exception(self, resadapter_name, name): \
            # pylint: disable=no-self-use
        raise ResourceNotFound(
            'Resource adapter configuration [{1}] does not exist for'
            ' resource adapter [{0}]'.format(resadapter_name, name))

    def get(self, session, resadapter_name, name):
        """Returns dict with resource adapter configuration

        Raises:
            ResourceNotFound
            ResourceAdapterNotFound
        """

        ResourceAdaptersDbHandler().getResourceAdapter(
            session, resadapter_name)

        entries = self.__get_query(session, resadapter_name, name).all()

        if not entries:
            self.__raise_not_found_exception(resadapter_name, name)

        result = dict(name=name,
                      resourceadapter=resadapter_name,
                      configuration=[])

        for entry in entries:
            result['configuration'].append(dict(key=str(entry.key),
                                                value=str(entry.value)))

        return result

    def get_profile_names(self, session, resadapter_name): \
            # pylint: disable=no-self-use
        """Return list of all profile names for specified resource adapter

        Raises:
            ResourceAdapterNotFound
        """

        # Validate resource adapter first
        ResourceAdaptersDbHandler().getResourceAdapter(
            session, resadapter_name)

        return [result.name
                for result in session.query(
                    ResourceAdapterCredential.name).join(
                        ResourceAdapter).filter(
                            ResourceAdapter.name ==
                            resadapter_name).distinct()]

    def __get_query(self, session, resadapter_name, name): \
            # pylint: disable=no-self-use

        return session.query(
            ResourceAdapterCredential).join(ResourceAdapter).filter(
                and_(ResourceAdapterCredential.name == name,
                     ResourceAdapter.name == resadapter_name))

    def create(self, session, resadapter_name, name, configuration):
        """Create new resource adapter configuration

        Raises:
            InvalidArgument
            ResourceAlreadyExists
            ResourceAdapterNotFound
        """

        if not configuration:
            raise InvalidArgument('Missing \'configuration\' argument(s)')

        # Check for any entry matching the specification
        if self.__get_query(session, resadapter_name, name).first():
            # Raise an exception if it exists...
            raise ResourceAlreadyExists(
                'Resource adapter configuration {1} already exists for'
                ' resource adapter {0}'.format(resadapter_name, name))

        adapter = \
            ResourceAdaptersDbHandler().getResourceAdapter(
                session, resadapter_name)

        # Create one ResourceAdapterCredentials record per key-value pair
        for entry in configuration:
            if 'key' not in entry or 'value' not in entry:
                raise InvalidArgument(
                    'Malformed resource adapter configuration data')

            # Initialize ResourceAdapterCredentials record
            cred = ResourceAdapterCredential(name=name,
                                             resourceadapter=adapter,
                                             key=entry['key'],
                                             value=entry['value'])

            # Add record to session
            session.add(cred)

    def delete(self, session, resadapter_name, name):
        """Delete resource adapter configuration"""

        ResourceAdaptersDbHandler().getResourceAdapter(
            session, resadapter_name)

        for entry in self.__get_query(session, resadapter_name, name).all():
            session.delete(entry)

    def update(self, session, resadapter_name, name, configuration):
        """Update an existing resource adapter configuration

        Raises:
            ResourceNotFound
            ResourceAdapterNotFound
        """

        adapter = \
            ResourceAdaptersDbHandler().getResourceAdapter(
                session, resadapter_name)

        if not self.__get_query(session, resadapter_name, name).first():
            # Resource adapter configuration does not exist
            self.__raise_not_found_exception(resadapter_name, name)

        for entry in configuration:
            if 'key' not in entry or 'value' not in entry:
                raise InvalidArgument(
                    'Malformed resource adapter configuration data')

            key = entry['key']
            value = entry['value']

            r = session.query(
                ResourceAdapterCredential).join(ResourceAdapter).filter(
                    and_(ResourceAdapterCredential.name == name,
                         ResourceAdapter.name == resadapter_name,
                         ResourceAdapterCredential.key == key)).first()

            if r and value is not None:
                # Update existing record with new value
                r.value = value
            elif r and value is None:
                # Delete existing record
                session.delete(r)
            elif value is not None:
                # Create new record
                r = ResourceAdapterCredential(name=name,
                                              resourceadapter=adapter,
                                              key=key,
                                              value=value)

                session.add(r)
