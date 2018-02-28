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

from tortuga.db.dbManager import DbManager
from tortuga.db.resourceAdapterCredentialsDbHandler \
    import ResourceAdapterCredentialsDbHandler


class ResourceAdapterConfigurationManager(object):
    def create(self, resadapter_name, name, configuration): \
            # pylint: disable=no-self-use
        """
        Raises:
            ResourceAlreadyExists
        """

        session = DbManager().openSession()

        try:
            ResourceAdapterCredentialsDbHandler().create(
                session, resadapter_name, name, configuration)

            session.commit()
        finally:
            DbManager().closeSession()

    def get(self, resadapter_name, name): \
            # pylint: disable=no-self-use
        """
        Raises:
            resourceNotFound
        """

        session = DbManager().openSession()

        try:
            return ResourceAdapterCredentialsDbHandler().get(
                session, resadapter_name, name)
        finally:
            DbManager().closeSession()

    def get_profile_names(self, resadapter_name): \
            # pylint: disable=no-self-use
        """
        Raises:
            resourceNotFound
        """

        session = DbManager().openSession()

        try:
            return ResourceAdapterCredentialsDbHandler().get_profile_names(
                session, resadapter_name)
        finally:
            DbManager().closeSession()

    def delete(self, resadapter_name, name): \
            # pylint: disable=no-self-use
        session = DbManager().openSession()

        try:
            ResourceAdapterCredentialsDbHandler().delete(
                session, resadapter_name, name)

            session.commit()
        finally:
            DbManager().closeSession()

    def update(self, resadapter_name, name, configuration): \
            # pylint: disable=no-self-use
        """
        Raises:
            ResourceNotFound
        """

        session = DbManager().openSession()

        try:
            ResourceAdapterCredentialsDbHandler().update(
                session, resadapter_name, name, configuration)

            session.commit()
        finally:
            DbManager().closeSession()
