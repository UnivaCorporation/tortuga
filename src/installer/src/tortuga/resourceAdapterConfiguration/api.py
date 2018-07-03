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
from typing import Dict, List

from sqlalchemy.orm.session import Session

from tortuga.exceptions.validationError import ValidationError
from . import validator
from .manager import ResourceAdapterConfigurationManager
from ..utility.tortugaApi import TortugaApi


class ResourceAdapterConfigurationApi(TortugaApi):
    def create(self, session: Session, resadapter_name: str, name: str,
               configuration: List[Dict[str, str]],
               force: bool = False):
        """
        Creates a new resource adapter profile.

        :param Session session:                    the current database
                                                   session
        :param str resadapter_name:                the name of the resource
                                                   adapter
        :param str name:                           the name of the resource
                                                   adapter profile
        :param List[Dict[str, str]] configuration: the list of configuration
                                                   settings
        :param bool force:                         when True, will not
                                                   validate the configuration
                                                   settings

        :raises ResourceAlreadyExists:
        :raises ResourceAdapterNotFound:
        :raises ValidationError:

        """
        self.getLogger().debug(
            'create(resadapter_name=[{}], name=[{}],'
            ' configuration=[...])'.format(resadapter_name, name))

        try:
            ResourceAdapterConfigurationManager().create(
                session, resadapter_name, name, configuration, force)

        except validator.ValidationError as ex:
            raise ValidationError(str(ex))

    def get(self, session, resadapter_name, name):
        self.getLogger().debug(
            'get(resadapter_name=[{}], name=[{}])'.format(
                resadapter_name, name))

        return ResourceAdapterConfigurationManager().get(
            session, resadapter_name, name)

    def get_profile_names(self, session, adapter_name):
        self.getLogger().debug('get_profile_names()')
        return ResourceAdapterConfigurationManager().get_profile_names(
            session, adapter_name)

    def delete(self, session, resadapter_name, name):
        self.getLogger().debug(
            'delete(resadapter_name=[{}], name=[{}])'.format(
                resadapter_name, name))

        ResourceAdapterConfigurationManager().delete(
            session, resadapter_name, name)

    def update(self, session: Session, resadapter_name: str, name: str,
               configuration: List[Dict[str, str]],
               force: bool = False):
        """
        Updates an existing resource adapter profile.

        :param Session session:                    the current database
                                                   session
        :param str resadapter_name:                the name of the resource
                                                   adapter
        :param str name:                           the name of the resource
                                                   adapter profile
        :param List[Dict[str, str]] configuration: the list of configuration
                                                   settings
        :param bool force:                         when True, will not
                                                   validate the configuration
                                                   settings

        :raises ResourceAlreadyExists:
        :raises ResourceAdapterNotFound:
        :raises ValidationError:

        """
        self.getLogger().debug(
            'update(resadapter_name=[{}], name=[{}],'
            ' configuration=[...])'.format(resadapter_name, name))

        try:
            ResourceAdapterConfigurationManager().update(
                session, resadapter_name, name, configuration, force)

        except validator.ValidationError as ex:
            raise ValidationError(str(ex))
