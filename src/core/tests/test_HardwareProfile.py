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

"""
These are very specific tests related to recent devel work. This is NOT
a comprehensive unit test for the HardwareProfile class
"""

from tortuga.objects.hardwareProfile import HardwareProfile


def test_serialization():
    hp = HardwareProfile()
    hp.setName('test')

    hp.setDefaultResourceAdapterConfig('resadapterconfig')

    hp_dict = hp.getCleanDict()

    assert hp_dict['name'] == 'test'

    assert 'default_resource_adapter_config' in hp_dict


def test_deserialization():
    name = 'testEXAMPLE'

    cfg_name = 'configEXAMPLE'

    hp_dict = {
        'name': name,
        'default_resource_adapter_config': cfg_name,
    }

    hp = HardwareProfile.getFromDict(hp_dict)

    assert hp.getName() == name

    assert hp.getDefaultResourceAdapterConfig() == cfg_name
