from typing import Type, Iterator, Optional

from tortuga.types.base import BaseType


class TypeStore:
    """
    Base class for storing objects.

    """
    #
    # The type class that this store is designed to work with
    #
    type_class: Type[BaseType] = BaseType

    def save(self, obj: BaseType) -> BaseType:
        """
        Saves the event to the store. If the object doesn't exist, it is
        created, otherwise it is updated.

        :param BaseType obj: the object instance to save

        :return BaseType: the object that was saved

        """
        raise NotImplementedError()

    def get(self, obj_id: str) -> Optional[BaseType]:
        """
        Gets an object from the store.

        :param str obj_id: the id of the object to retrieve

        :return: the object instance, if found, otherwise None

        """
        raise NotImplementedError()

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[BaseType]:
        """
        Gets a iterator of objects from the event store.

        :param str order_by:     the name of the object attribute to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)
        :param int limit:        the number of objects to limit in the
                                 iterator
        :param filters:          one or more filters to apply to the list

        :return Iterator[BaseType]: an iterator of objects

        """
        raise NotImplementedError()
