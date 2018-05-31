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

from typing import Dict, List, Tuple, Union

from sqlalchemy.orm.session import Session

from tortuga.db.models.resourceAdapterConfig import ResourceAdapterConfig
from tortuga.db.models.resourceAdapterSetting import ResourceAdapterSetting
from tortuga.db.resourceAdapterConfigDbHandler import \
    ResourceAdapterConfigDbHandler
from tortuga.db.resourceAdaptersDbHandler import ResourceAdaptersDbHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists
from tortuga.exceptions.resourceNotFound import ResourceNotFound


class ResourceAdapterConfigurationManager:
    def __init__(self):
        self._resourceAdapterConfigDbHandler = \
            ResourceAdapterConfigDbHandler()

        self._resourceAdaptersDbHandler = ResourceAdaptersDbHandler()

    def create(self, session: Session, resadapter_name: str, name: str,
               configuration: Union[List[Dict[str, str]], None] = None) \
            -> ResourceAdapterConfig:
        """
        Raises:
            ResourceAlreadyExists
            ResourceAdapterNotFound
        """

        adapter = self._resourceAdaptersDbHandler.getResourceAdapter(
            session, resadapter_name)

        try:
            self._resourceAdapterConfigDbHandler.get(
                session, resadapter_name, name)

            raise ResourceAlreadyExists(
                'Resource adapter configuration [{}] already exists'.format(
                    name
                )
            )
        except ResourceNotFound:
            # good!
            pass

        cfg = ResourceAdapterConfig(name=name)

        for entry in configuration or []:
            cfg.settings.append(
                ResourceAdapterSetting(
                    key=entry['key'],
                    value=entry['value']
                )
            )

        adapter.resource_adapter_config.append(cfg)

        return cfg

    def get(self, session: Session, resadapter_name: str, name: str) \
            -> ResourceAdapterConfig:
        """
        Raises:
            ResourceNotFound
            ResourceAdapterNotFound
        """

        # first check if resource adapter exists
        self._resourceAdaptersDbHandler.getResourceAdapter(
            session, resadapter_name)

        # then attempt to retrieve specified configuration
        return self._resourceAdapterConfigDbHandler.get(
            session, resadapter_name, name)

    def get_profile_names(self, session: Session, resadapter_name: str) \
            -> List[str]:
        """
        Raises:
            ResourceAdapterNotFound
        """

        adapter = self._resourceAdaptersDbHandler.getResourceAdapter(
            session, resadapter_name
        )

        return [cfg.name for cfg in adapter.resource_adapter_config]

    def delete(self, session: Session, resadapter_name: str, name: str) \
            -> None:
        """
        Delete resource adapter configuration

        Raises:
            ResourceAdapterNotFound
            ResourceNotFound
        """

        self._resourceAdaptersDbHandler.getResourceAdapter(
            session, resadapter_name)

        cfg = self.get(session, resadapter_name, name)

        session.delete(cfg)

    def update(self, session: Session, resadapter_name: str, name: str,
               configuration: List[Dict[str, str]]) -> None:
        """
        Update an existing resource adapter configuration

        Raises:
            ResourceNotFound
            ResourceAdapterNotFound
        """

        # ensure resource adapter is valid
        self._resourceAdaptersDbHandler.getResourceAdapter(
            session, resadapter_name)

        cfg = self._resourceAdapterConfigDbHandler.get(
            session, resadapter_name, name)

        self.__update_settings(session, configuration, cfg.settings)

        session.commit()

    def __update_settings(self, session: Session,
                          configuration: List[Dict[str, str]],
                          existing_settings: List[ResourceAdapterSetting]) \
            -> None:
        new_settings: List[Tuple[str, str]] = []
        delete_settings: List[ResourceAdapterSetting] = []

        for entry in configuration:
            if 'key' not in entry or 'value' not in entry:
                raise InvalidArgument(
                    'Malformed resource adapter configuration data')

            setting = setting_exists(existing_settings, entry['key'])
            if setting is None:
                # create new setting
                new_settings.append((entry['key'], entry['value']))

                continue

            if entry['value'] is None:
                # setting is marked for deletion
                delete_settings.append(setting)

                continue

            # update existing settings
            setting.value = entry['value']

        # add new setting(s)
        for key, value in new_settings:
            existing_settings.append(
                ResourceAdapterSetting(key=key, value=value)
            )

        # delete setting(s) marked for deletion
        for delete_setting in delete_settings:
            session.delete(delete_setting)


def setting_exists(settings: List[ResourceAdapterSetting], key: str) \
        -> Union[ResourceAdapterSetting, None]:
    for setting in settings:
        if setting.key == key:
            return setting

    return None
