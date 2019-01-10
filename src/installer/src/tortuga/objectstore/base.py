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

from logging import getLogger
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from tortuga.logging import OBJECT_STORE_NAMESPACE


logger = getLogger(OBJECT_STORE_NAMESPACE)


def cmp_equals(left: Any, right: Any):
    return left == right


def cmp_greater_than(left: Any, right: Any):
    return left > right


def cmp_less_than(left: Any, right: Any):
    return left < right


COMPARATORS = {
    'eq': cmp_equals,
    'gt': cmp_greater_than,
    'lt': cmp_less_than,
}


def matches_filters(obj: Union[object, dict],
                    filters: Dict[str, Any]) -> bool:
    """
    Determines whether or not an object matches a list of filters. Filters
    look like this:

        attr=value
        attr__lt=valiue
        attr__attr__gt=value

    Where attr is an attribute name on the object (dict), which can be
    nested using multiple levels of "__". The last part of the filter is
    a comparator (see COMPARATORS). If no comparator is provided, then
    equality is assumed.

    :param Union[object, dict] obj: the object or dict to test
    :param Dict[str, Any] filters:  the list of filters to test

    :raises KeyError: if the attribute does not exist

    :return bool: True if all filters match (or no filters provided),
                  False otherwise

    """
    result = True

    for k, right in filters.items():
        parts = k.split('__')
        if parts[-1] in COMPARATORS.keys():
            comparator = parts.pop()
        else:
            comparator = 'eq'

        left = obj
        for attr in parts:
            if isinstance(left, dict):
                if attr not in left.keys():
                    return False
                left = left[attr]
            else:
                if not hasattr(left, attr):
                    return False
                left = getattr(left, attr)

        if not COMPARATORS[comparator](left, right):
            result = False

    return result


class ObjectStore:
    def __init__(self, namespece: str):
        """
        Initialization.

        :param str namespece: a namespace to use for these objects

        """
        self._namespace = namespece

    def get_key_name(self, key: str) -> str:
        """
        Builds the object store key name to be used for storing the object.

        :param str key: the key name to use as the base

        :return str: the object store key name

        """
        return '{}:{}'.format(self._namespace, key)

    def set(self, key: str, value: dict):
        """
        Saves the object to the object store.

        :param str key:    the key name to use for the object
        :param dict value: the object to store, stores {} if None

        """
        raise NotImplementedError()

    def get(self, key: str) -> Optional[dict]:
        """
        Gets the object from the object store.

        :param str key: the key of the object to get

        :return: the object, None if not found

        """
        raise NotImplementedError()

    def list(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False,
            limit: Optional[int] = None,
            **filters) -> Iterator[Tuple[str, dict]]:
        """
        Gets a list of objects from the object store.

        :param str order_by:     the name of the object attribute to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)
        :param int limit:        the number of objects to limit in the
                                 iterator
        :param filters:          one or more filters to apply to the list

        :return List[Tuple[str, dict]]: an iterator of tuples, containing
                                        (key, object)

        """
        logger.debug(
            'list(order_by={}, order_desc={}, order_alpha={}, limit={}, filters={}) -> ...'.format(
                order_by, order_desc, order_alpha, limit, filters
            )
        )

        count = 0
        for key, obj in self.list_sorted(order_by=order_by,
                                         order_desc=order_desc,
                                         order_alpha=order_alpha):
            if matches_filters(obj, filters):
                count += 1
                if limit and count == limit:
                    yield (key, obj)
                    return

                yield (key, obj)

    def list_sorted(
            self,
            order_by: Optional[str] = None,
            order_desc: bool = False,
            order_alpha: bool = False) -> Iterator[Tuple[str, dict]]:
        """
        Returns a sorted iterator of objects. This method is designed to be
        called by the list() method, which is responsible for applying
        the limits and filters.

        :param int order_by:     the name of the object attribue to order by
        :param bool order_desc:  sort in descending order
        :param bool order_alpha: order alphabetically (instead of numerically)

        :return List[Tuple[str, dict]]: a sorted iterator of tuples,
                                        containing (key, object)

        """
        raise NotImplementedError()

    def delete(self, key: str):
        """
        Deletes an object from the object store.

        :param str key: the key of the object to delete

        """
        raise NotImplementedError()

    def exists(self, key: str) -> bool:
        """
        Determines whether or not a key exists.

        :param str key: the key to check for
        :return bool: True if it exists, False otherwise

        """
        raise NotImplementedError()
