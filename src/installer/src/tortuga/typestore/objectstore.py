import logging
from typing import Iterator, Optional

from tortuga.objectstore.base import matches_filters, ObjectStore
from tortuga.types.base import BaseType
from .base import TypeStore


logger = logging.getLogger(__name__)


class ObjectStoreTypeStore(TypeStore):
    """
    An implementation of the type store that saves data in an object store.

    """
    def __init__(self, object_store: ObjectStore):
        self._store = object_store
    
    def marshall(self, obj: BaseType) -> dict:
        """
        Marshalls a obj into a dict.

        :param BaseType obj: the obj instance to marshall

        :return dict: the marshalled data

        """
        marshalled = obj.schema().dump(obj)
        return marshalled.data

    def unmarshall(self, obj_dict: dict) -> BaseType:
        """
        Unmarshalls an obj dict into an obj class instance.

        :param dict obj_dict:
        :return BaseType: the unmarshalled obj

        """
        unmarshalled = self.type_class.schema().load(obj_dict)
        return self.type_class(**unmarshalled.data)

    def save(self, obj: BaseType) -> BaseType:
        """
        See superclass.

        :param BaseType obj:

        """
        self._store.set(obj.id, self.marshall(obj))
        return self.get(obj.id)

    def get(self, obj_id: str) -> Optional[BaseType]:
        """
        See superclass.

        :param str obj_id:

        :return BaseType:

        """
        obj_dict = self._store.get(obj_id)
        if obj_dict is None:
            return None
        return self.unmarshall(obj_dict)

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[BaseType]:
        """
        See superclass.

        :return Iterator[BaseType]:

        """
        logger.debug(
            'list(order_by={}, order_desc={}, limit, filters={}) -> ...'.format(
                order_by, order_desc, limit, filters
            )
        )

        count = 0
        for _, obj_dict in self._store.list_sorted(order_by=order_by,
                                                   order_desc=order_desc,
                                                   order_alpha=order_alpha):
            obj = self.unmarshall(obj_dict)
            if matches_filters(obj, filters):
                count += 1
                if limit and count == limit:
                    yield obj
                    return

                yield obj
