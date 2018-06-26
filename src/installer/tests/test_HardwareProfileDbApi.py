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

from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.exceptions.hardwareProfileNotFound import HardwareProfileNotFound
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.objects.hardwareProfile import HardwareProfile

hardwareProfileDbApi = HardwareProfileDbApi()


def test_getHardwareProfile(dbm):
    """
    Get hardware profile with default resource adapter configuration
    defined.
    """

    name = 'aws'

    result = HardwareProfileDbApi().getHardwareProfile(name)

    assert isinstance(result, HardwareProfile)

    assert result.getName() == name

    assert result.getDefaultResourceAdapterConfig() is None

    assert result.getResourceAdapter()


def test_getHardwareProfile_alt(dbm):
    """
    Get hardware profile with default resource adapter configuration
    defined.
    """

    name = 'aws2'

    result = HardwareProfileDbApi().getHardwareProfile(name)

    assert isinstance(result, HardwareProfile)

    assert result.getName() == name

    # 'nondefault' is the known default resource adapter configuration
    # profile for the hardware profile 'aws2'
    assert result.getDefaultResourceAdapterConfig() == 'nondefault'

    assert result.getResourceAdapter()


def test_getHardwareProfile_failed(dbm):
    with pytest.raises(HardwareProfileNotFound):
        HardwareProfileDbApi().getHardwareProfile('doesnotexistEXAMPLE')


def test_updateHardwareProfile_resource_adapter_config(dbm):
    """
    Update existing hardware profile
    """

    name = 'aws'

    hwprofile = hardwareProfileDbApi.getHardwareProfile(name)

    assert not hwprofile.getDefaultResourceAdapterConfig()

    # update resource adapter config to 'nondefault' (preexisting)
    hwprofile.setDefaultResourceAdapterConfig('nondefault')

    hardwareProfileDbApi.updateHardwareProfile(hwprofile)

    # get updated hardware profile
    hwprofile_updated = hardwareProfileDbApi.getHardwareProfile(name)

    # ensure resource adapter config has been updated
    assert hwprofile_updated.getDefaultResourceAdapterConfig() == 'nondefault'

    # clear resource adapter config
    hwprofile_updated.setDefaultResourceAdapterConfig(None)

    hardwareProfileDbApi.updateHardwareProfile(hwprofile_updated)

    # validate updated hardware profile
    hwprofile_updated2 = hardwareProfileDbApi.getHardwareProfile(name)

    assert not hwprofile_updated2.getDefaultResourceAdapterConfig()


def test_updateHardwareProfile_resource_adapter_config_invalid(dbm):
    """
    Attempt to update existing hardware profile with invalid resource
    adapter configuration profile.
    """

    name = 'aws'

    hwprofile = hardwareProfileDbApi.getHardwareProfile(name)

    assert not hwprofile.getDefaultResourceAdapterConfig()

    # update resource adapter config to 'nondefault' (preexisting)
    hwprofile.setDefaultResourceAdapterConfig('doesnotexistEXAMPLE')

    with pytest.raises(InvalidArgument):
        hardwareProfileDbApi.updateHardwareProfile(hwprofile)


def test_addHardwareProfile(dbm):
    """
    Add new hardware profile
    """

    hwprofile = HardwareProfile()
    hwprofile.setName('example')
    hwprofile.setNameFormat('compute-#NN')

    hardwareProfileDbApi.addHardwareProfile(hwprofile)

    stored_hwprofile = hardwareProfileDbApi.getHardwareProfile(hwprofile.getName())

    assert stored_hwprofile.getName() == hwprofile.getName()

    hardwareProfileDbApi.updateHardwareProfile(stored_hwprofile)

