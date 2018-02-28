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


logger = getLogger(__name__)


TABLE_MAPPER_REGISTRY = []


def register_table_mapper(table_mapper_class):
    """
    Registers a database table.

    :param table_mapper_class: an subclass of TableMapper

    """
    if table_mapper_class in TABLE_MAPPER_REGISTRY:
        return
    TABLE_MAPPER_REGISTRY.append(table_mapper_class)
    logger.info('Database table registered: {}'.format(
        table_mapper_class.__name__))


def get_all_table_mappers():
    """
    Gets a list of all web database tables

    :return: a list of web service controller instances

    """
    return [tm for tm in TABLE_MAPPER_REGISTRY]
