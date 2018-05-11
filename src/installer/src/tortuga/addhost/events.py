from marshmallow import fields

from tortuga.events.base import BaseEventSchema, BaseEvent


class AddNodeRequestQueuedSchema(BaseEventSchema):
    request_id = fields.String()


class AddNodeRequestQueued(BaseEvent):
    name = 'add-node-request-queued'
    schema = AddNodeRequestQueuedSchema

    def __init__(self, request_id: str, **kwargs):
        self.request_id: str = request_id
        super().__init__(**kwargs)


class DeleteNodeRequestQueuedSchema(BaseEventSchema):
    transaction_id = fields.String()


class DeleteNodeRequestQueued(BaseEvent):
    name = 'delete-node-request-queued'
    schema = DeleteNodeRequestQueuedSchema

    def __init__(self, transaction_id: str, **kwargs):
        self.transaction_id: str = transaction_id
        super().__init__(**kwargs)
