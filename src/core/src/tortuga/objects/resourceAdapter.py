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

from tortuga.objects.tortugaObject import TortugaObject
from .resource_adapter_settings import get_setting_class


class ResourceAdapter(TortugaObject): \
        # pylint: disable=too-many-public-methods

    ROOT_TAG = 'resourceadapter'

    def __init__(self, name=None, kitId=None, settings=None):
        if not settings:
            settings = {}

        super().__init__(
            {'name': name, 'kitId': kitId, 'settings': settings},
            ['id', 'name'],
            ResourceAdapter.ROOT_TAG
        )

    def __repr__(self):
        return self.getName()

    def getId(self):
        return self['id']

    def setId(self, id_):
        self['id'] = id_

    def getName(self):
        return self['name']

    def setName(self, name):
        self['name'] = name

    def getKitId(self):
        return self['kitId']

    def setKitId(self, kitId):
        self['kitId'] = kitId

    def get_settings(self):
        return self['settings']

    def set_settings(self, settings):
        if not settings:
            settings = {}

        self['settings'] = settings

    @staticmethod
    def getKeys():
        return ['id', 'name', 'kitId', 'settings']

    @classmethod
    def getFromDict(cls, _dict, ignore=None):
        inst = cls()

        for key in cls.getKeys():
            if key not in _dict:
                inst[key] = None

            elif key == 'settings':
                inst[key] = cls.deserialize_settings(_dict[key])

            else:
                inst[key] = _dict[key]

        return inst

    @classmethod
    def deserialize_settings(cls, settings_dict: dict) -> dict:
        if not settings_dict:
            settings_dict = {}

        deserialized_settings_dict = {}

        for key, setting in settings_dict.items():
            setting_class = get_setting_class(setting['type'])
            schema = setting_class.schema()
            deserialized_settings_dict[key] = schema.load(setting)

        return deserialized_settings_dict

    def getCleanDict(self):
        data_dict = super().getCleanDict()
        data_dict['settings'] = self.serialize_settings()
        return data_dict

    def serialize_settings(self):
        serialized_settings_dict = {}

        for key, setting in self.get_settings().items():
            setting_class = get_setting_class(setting.type)
            schema = setting_class.schema()
            serialized_settings_dict[key] = schema.dump(setting).data

        return serialized_settings_dict
