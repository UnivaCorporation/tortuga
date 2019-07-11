# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Tags 2.0 (the "License");
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

from marshmallow import fields

from .base import BaseEvent, BaseEventSchema


class HardwareProfileTagsChangedSchema(BaseEventSchema):
    """
    Schema for the HardwareProfileTagsChanged events.

    """
    hardwareprofile_id = fields.String()
    hardwareprofile_name = fields.String()
    tags = fields.Dict()
    previous_tags = fields.Dict()


class HardwareProfileTagsChanged(BaseEvent):
    """
    Event that fires when a hardware profile tags are changed.

    """
    name = 'hardware-profile-tags-changed'
    schema_class = HardwareProfileTagsChangedSchema

    def __init__(self, hardwareprofile_id: str, hardwareprofile_name: str,
                 tags: dict, previous_tags: dict, **kwargs):
        """
        Initializer.

        :param dict hardware_profile: the current state of the hardware
                                      profile
        :param dict previous_tags: the previous version of the tags for the
                                   hardware profile
        :param kwargs:

        """
        super().__init__(**kwargs)
        self.hardwareprofile_id = hardwareprofile_id
        self.hardwareprofile_name = hardwareprofile_name
        self.tags = tags
        self.previous_tags = previous_tags
