from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from .base import ModelBase


class NodeTag(ModelBase):
    __tablename__ = 'node_tags'
    __table_args__ = (
        UniqueConstraint('node_id', 'tag_id'),
    )

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
