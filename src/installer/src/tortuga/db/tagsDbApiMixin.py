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

from typing import Dict

from .models.base import ModelBase
from .models.tagMixin import TagMixin


class TagsDbApiMixin:
    """
    A mixin for tagging database models.

    """
    #
    # The the tag model to use
    #
    tag_model: TagMixin = None

    def _set_tags(self, db_instance: ModelBase,
                  tags: Dict[str, str], merge: bool = False):
        """
        Sets the tags on a database model instance to a specified list. The
        model for this instance is expected to have a FK relationship to
        a tags model.

        :param db_instance: a database model instance
        :param tags:        a dictionary of tags to set on this instance
        :param merge:       if True, the provided tags are merged into the
                            existing list of tags for the model instance;
                            otherwise, any tags in the db but not in the
                            tags dict will be removed

        """
        #
        # Make sure a null/None value is handled correctly
        #
        if not tags:
            tags = {}

        #
        # Store current list of tags in an array so we can keep track
        # of which ones will need to be deleted
        #
        tags_to_delete = {tag.name: tag for tag in db_instance.tags}

        for name, value in tags.items():
            if name in tags_to_delete.keys():
                #
                # Remove it from the to-delete list because we still need to
                # keep it
                #
                tag = tags_to_delete.pop(name)
                #
                # Re-set the value, in case it has changed
                #
                tag.value = value

            else:
                db_instance.tags.append(
                    self.tag_model(name=name, value=value)
                )

        #
        # Anything left in current_tags was not part of the tags dict, and
        # thus needs to be removed, unless we are doing a merge
        #
        if not merge:
            for tag in tags_to_delete.values():
                db_instance.tags.remove(tag)
