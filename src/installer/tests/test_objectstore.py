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

import types

from tortuga.objectstore.base import matches_filters
from tortuga.objectstore.redis import RedisObjectStore


data_1 = {
    'string': 'bar',
    'integer': 2,
    'float': 1.34,
    'dict': {
        'string': 'Bob',
        'integer': 15,
        'float': 5.67,
        'list': [6, 7, 8]
    },
    'list': [1, 2, 3, 4]
}


data_2 = {
    'foo': 'bar',
    'id': 99,
}


def test_set_exists_get_delete(redis):
    store = RedisObjectStore(namespace='test', redis_client=redis)

    #
    # Assert that what we put in is what we get out
    #
    store.set('my_key', data_1)

    #
    # Assert that the object exists in the store
    #
    assert store.exists('my_key')

    #
    # Assert that what we put in is what we get out
    #
    assert store.get('my_key') == data_1

    #
    # Assert that a deletion actually deletes the object
    #
    store.delete('my_key')
    assert not store.exists('my_key')
    assert store.get('my_key') is None


def test_namespace(redis):
    store_1 = RedisObjectStore(namespace='test_1', redis_client=redis)
    store_2 = RedisObjectStore(namespace='test_2', redis_client=redis)

    #
    # Assert that there are no name collisions for different namespaces
    #
    store_1.set('my_key', data_1)
    store_2.set('my_key', data_2)
    assert store_1.get('my_key') == data_1
    assert store_2.get('my_key') == data_2

    #
    # Assert that objects added to one namespace do not show up in another
    #
    store_1.set('another_key', data_1)
    assert not store_2.exists('another_key')
    assert store_2.get('another_key') is None


def test_list(redis):
    store = RedisObjectStore(namespace='test', redis_client=redis)

    #
    # Populate the store with some objects
    #
    to_store = {
        'my_key1': data_1,
        'my_key2': data_2
    }
    for k, v in to_store.items():
        store.set(k, v)

    #
    # Make sure we get everything out using the list function
    #
    from_store = {}
    for k, v in store.list():
        from_store[k] = v
    assert to_store == from_store


def test_list_limit(redis):
    store = RedisObjectStore(namespace='test', redis_client=redis)

    #
    # Populate the store with some objects
    #
    to_store = {
        'my_key1': data_1,
        'my_key2': data_2,
        'my_key3': data_1,
        'my_key4': data_2,
        'my_key5': data_1
    }
    for k, v in to_store.items():
        store.set(k, v)

    #
    # Make sure we get don't get more objects back than limit
    #
    from_store = []
    for k, v in store.list(limit=3):
        from_store.append(v)
    assert len(from_store) == 3

    #
    # Make sure there are no problems if we set the limit higher than
    # what we expect to get back
    #
    from_store = []
    for k, v in store.list(limit=10):
        from_store.append(v)
    assert len(from_store) == 5


def test_list_sort(redis):
    store = RedisObjectStore(namespace='test', redis_client=redis)

    #
    # Populate the store with some objects
    #
    to_store = {
        'my_key5': {'number': 5, 'name': 'alice'},
        'my_key2': {'number': 2, 'name': 'bob'},
        'my_key1': {'number': 1, 'name': 'zeph'},
        'my_key4': {'number': 4, 'name': 'fred'},
        'my_key3': {'number': 3, 'name': 'joe'}
    }
    for k, v in to_store.items():
        store.set(k, v)

    #
    # Test sorting in ascending order
    #
    numbers = []
    for k, v in store.list(order_by='number'):
        numbers.append(v['number'])
    assert numbers == [1, 2, 3, 4, 5]

    names = []
    for k, v in store.list(order_by='name'):
        names.append(v['name'])
    assert names == ['alice', 'bob', 'fred', 'joe', 'zeph']

    #
    # Test sorting in descending order
    #
    numbers = []
    for k, v in store.list(order_by='number', order_alpha=True,
                           order_desc=True):
        numbers.append(v['number'])
    assert numbers == [5, 4, 3, 2, 1]

    names = []
    for k, v in store.list(order_by='name', order_alpha=True,
                           order_desc=True):
        names.append(v['name'])
    assert names == ['zeph', 'joe', 'fred', 'bob', 'alice']


def test_filter_matches():
    my_dict = {
        'number': 45,
        'name': 'bob',
        'stats': {
            'age': 32
        }
    }

    my_obj = types.SimpleNamespace()
    my_obj.number = 45
    my_obj.name = 'bob'
    my_obj.stats = types.SimpleNamespace()
    my_obj.stats.age = 32
    
    #
    # Test equality
    #
    filters = {
        'number': 45,
        'name': 'bob'
    }
    assert matches_filters(my_dict, filters)
    assert matches_filters(my_obj, filters)
    
    #
    # Test less than
    #
    filters = {
        'number__lt': 46,
    }
    assert matches_filters(my_dict, filters)
    assert matches_filters(my_obj, filters)
    
    #
    # Test greater than
    #
    filters = {
        'name__gt': 'abba',
    }
    assert matches_filters(my_dict, filters)
    assert matches_filters(my_obj, filters)

    #
    # Test nested attributes
    #
    filters = {
        'stats__age__gt': 30,
    }
    assert matches_filters(my_dict, filters)
    assert matches_filters(my_obj, filters)


def test_list_filter(redis):
    store = RedisObjectStore(namespace='test', redis_client=redis)

    #
    # Populate the store with some objects
    #
    to_store = {
        'my_key5': {'number': 5, 'name': 'alice', 'age': 22},
        'my_key2': {'number': 2, 'name': 'bob', 'age': 33},
        'my_key1': {'number': 1, 'name': 'zeph', 'age': 44},
        'my_key4': {'number': 4, 'name': 'fred', 'age': 55},
        'my_key3': {'number': 3, 'name': 'joe', 'age': 33}
    }
    for k, v in to_store.items():
        store.set(k, v)

    #
    # Test equality
    #
    numbers = []
    for k, v in store.list(name='bob'):
        numbers.append(v['number'])
    assert numbers == [2]

    #
    # Test less than
    #
    numbers = []
    for k, v in store.list(order_by='number', age__lt=35):
        numbers.append(v['number'])
    assert numbers == [2, 3, 5]

    #
    # Test greater than
    #
    numbers = []
    for k, v in store.list(order_by='number', age__gt=40):
        numbers.append(v['number'])
    assert numbers == [1, 4]
