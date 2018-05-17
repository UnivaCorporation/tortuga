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
