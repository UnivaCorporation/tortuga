from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import ModelBase


class NodeRequest(ModelBase):
    __tablename__ = 'node_requests'

    id = Column(Integer, primary_key=True)
    request = Column(Text, nullable=False)
    timestamp = Column(DateTime)
    last_update = Column(DateTime)
    state = Column(String(255), nullable=False, default='pending')
    addHostSession = Column(String(36))
    message = Column(Text)
    admin_id = Column(Integer, ForeignKey('admins.id'))
    action = Column(String(255), nullable=False)

    owner = relationship('Admin')

    def __init__(self, node_request=None):
        super().__init__()

        self.request = node_request
