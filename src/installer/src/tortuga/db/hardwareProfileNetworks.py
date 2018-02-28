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

# pylint: disable=not-callable,multiple-statements

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relation, mapper

from tortuga.db.networks import Networks
from tortuga.db.networkDevices import NetworkDevices


class HardwareProfileNetworks(object): \
        # pylint: disable=too-few-public-methods

    def __init__(self, hardwareProfileId=None, networkId=None,
                 networkDeviceId=None):
        self.hardwareProfileId = hardwareProfileId
        self.networkId = networkId
        self.networkDeviceId = networkDeviceId

    def __repr__(self):
        return (
            '<HardwareProfileNetworks(hardwareProfileId=[%s], '
            'networkId=[%s], networkDeviceId=[%s])>'
            % (self.hardwareProfileId, self.networkId,
               self.networkDeviceId))
