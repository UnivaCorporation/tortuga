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

import pytest

from tortuga.exceptions.resourceAdapterNotFound import ResourceAdapterNotFound
from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists
from tortuga.exceptions.resourceNotFound import ResourceNotFound
from tortuga.resourceAdapterConfiguration.manager import \
    ResourceAdapterConfigurationManager


mgr = ResourceAdapterConfigurationManager()


def test_get_profile_names(dbm):
    with dbm.session() as session:
        result = mgr.get_profile_names(session, 'aws')

        assert isinstance(result, list) and 'default' in result


def test_get_profile_names_failed(dbm):
    with dbm.session() as session:
        with pytest.raises(ResourceAdapterNotFound):
            mgr.get_profile_names(session, 'nonexistent')


def test_create_duplicate(dbm):
    with dbm.session() as session:
        with pytest.raises(ResourceAlreadyExists):
            mgr.create(session, 'aws', 'default')

        session.commit()


def test_create_unique(dbm):
    cfg_name = 'test_default'

    with dbm.session() as session:
        mgr.create(session, 'aws', cfg_name, [{
            'key': 'test_default_key',
            'value': 'test_default_value',
        }], True)

        session.commit()

        cfg = mgr.get(session, 'aws', cfg_name)

        assert cfg.name == cfg_name

        for setting in cfg.configuration:
            if setting.key == 'test_default_key':
                break
        else:
            assert 0, "Setting not found"

        mgr.delete(session, 'aws', cfg_name)

        session.commit()

        with pytest.raises(ResourceNotFound):
            mgr.get(session, 'aws', cfg_name)
