from marshmallow import fields

from .base import BaseEvent, BaseEventSchema


class BaseTagSchema(BaseEventSchema):
    """
    Schema for the TagCreated events.

    """
    tag_id = fields.String()
    value = fields.String()


class BaseTagEvent(BaseEvent):
    """
    Event that fires when stuff happens to tags.

    """
    def __init__(self, **kwargs):
        """
        Initializer.

        :param str tag_id:      the ID of the tag
        :param str object_type: the object type that the tag points to
        :param str object_id:   the object id that the tag points to
        :param str name:        the name of the tag
        :param str value:       the value of the tag

        """
        super().__init__(**kwargs)
        self.tag_id: str = kwargs.get('tag_id', None)
        self.value: str = kwargs.get('value', None)


class TagCreated(BaseTagEvent):
    """
    Event that fires when a tag is created.

    """
    name = 'tag-created'
    schema_class = BaseTagSchema


class TagUpdatedSchema(BaseEventSchema):
    previous_value = fields.String()


class TagUpdated(BaseTagEvent):
    """
    Event that fires when a tag is updated.

    """
    name = 'tag-updated'
    schema_class = TagUpdatedSchema

    def __init__(self, **kwargs):
        """
        Initializer.

        :param str previous_name:  the previous name of the tag
        :param str previous_value: the previous value of the tag
        :param kwargs:             see superclass for additional params

        """
        super().__init__(**kwargs)
        self.previous_value: str = kwargs.get('previous_value', None)


class TagDeleted(BaseTagEvent):
    """
    Event that fires when a tag is created.

    """
    name = 'tag-deleted'
    schema_class = BaseTagSchema
