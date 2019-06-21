# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Tags 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, hardware
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
    hardware_profile = fields.Dict()
    previous_tags = fields.Dict()


class HardwareProfileTagsChanged(BaseEvent):
    """
    Event that fires when a hardware profile tags are changed.

    """
    name = 'hardware-profile-tags-changed'
    schema = HardwareProfileTagsChangedSchema

    def __init__(self, hardware_profile: dict, previous_tags: dict,
                 **kwargs):
        """
        Initializer.

        :param dict hardware_profile: the current state of the hardware
                                      profile
        :param dict previous_tags: the previous version of the tags for the
                                   hardware profile
        :param kwargs:

        """
        self.hardware_profile: dict = hardware_profile
        self.previous_hardware_profile: dict = previous_tags

        super().__init__(**kwargs)
