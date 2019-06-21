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


class SoftwareProfileTagsChangedSchema(BaseEventSchema):
    """
    Schema for the SoftwareProfileTagsChanged events.

    """
    software_profile = fields.Dict()
    previous_tags = fields.Dict()


class SoftwareProfileTagsChanged(BaseEvent):
    """
    Event that fires when a software profile tags are changed.

    """
    name = 'software-profile-tags-changed'
    schema = SoftwareProfileTagsChangedSchema

    def __init__(self, software_profile: dict, previous_tags: dict,
                 **kwargs):
        """
        Initializer.

        :param dict software_profile: the current state of the software
                                      profile
        :param dict previous_tags: the previous version of the tags for the
                                   software profile
        :param kwargs:

        """
        self.software_profile: dict = software_profile
        self.previous_software_profile: dict = previous_tags

        super().__init__(**kwargs)
