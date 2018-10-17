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
                  tags: Dict[str, str]):
        """
        Sets the tags on a database model instance to a specified list. The
        model for this instance is expected to have a FK relationship to
        a tags model.

        :param db_instance: a database model instance
        :param tags:        a dictionary of tags to set on this instance

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
        # thus needs to be removed
        #
        for tag in tags_to_delete.values():
            db_instance.tags.remove(tag)
