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

from typing import Dict

from datetime import datetime
import random
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.nicNotFound import NicNotFound


class StopWatch(object):
    """
    Time the duration of a block of code.
    """
    def __enter__(self):
        """
        Called when the `with` block is started.

        :return: StopWatch instance
        """
        self._start = datetime.utcnow()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Called when the `with` block is terminated.

        :param exception_type: Exception
        :param exception_value: Exception
        :param traceback: Traceback
        :return: None
        """
        self.result = datetime.utcnow() - self._start


def iter_provisioning_nics(nics):
    for nic in nics:
        if not nic.ip:
            # Provisioning nic must have ip
            continue

        if not nic.network and not nic.boot:
            # nics without associated network use 'boot' to indicate
            # provisioning interface (aka internal interface)
            continue

        if nic.network and nic.network.type != 'provision':
            continue

        yield nic


def get_provisioning_nics(node):
    # Return a list of Nics objects that have an IP, network, and
    # network is a provisioning network.
    return [tmpnic for tmpnic in iter_provisioning_nics(node.nics)]


def get_provisioning_hwprofilenetwork(hardwareprofile):
    """
    Return the hardware profile provisioning network

    Raises:
        NetworkNotFound
    """

    for hardwareprofilenetwork in hardwareprofile.hardwareprofilenetworks:
        if hardwareprofilenetwork.network.type == 'provision':
            return hardwareprofilenetwork

    raise NetworkNotFound(
        'Hardware profile [%s] does not have a provisioning network' % (
            hardwareprofile.name))


def get_provisioning_nic(node):
    """
    Raises:
        NicNotFound
    """

    # Iterate over all nics associated with node, return first nic
    # marked as a provisioning nic or first nic without an assigned
    # ip address.

    prov_nics = get_provisioning_nics(node)

    if not prov_nics:
        raise NicNotFound(
            'Node [%s] does not have a provisioning NIC' % (node.name))

    return prov_nics[0]


def get_hwprofile_provisioning_nic(hardwareprofile):
    """
    Raises:
        HardwareProfileNotFound
    """

    return get_provisioning_hwprofilenetwork(
        hardwareprofile).hardwareprofile.nics[0]


def get_random_sleep_time(max_sleep_time=10000, sleep_interval=2000,
                          retries=0):
    """
    Random exponential backoff algorithm used to determine interval when
    polling to prevent overlapping requests

    :param max_sleep_time: maximum sleep time in milliseconds
    :param sleep_interval: maximum sleep interval
    :param retries: number of retries (used when looping)
    :return: milliseconds to sleep

    """
    temp = min(max_sleep_time, sleep_interval * 2 ** retries)

    return temp / 2 + random.randint(0, temp / 2)


def patch_managed_tags(tags: Dict[str, str]) -> Dict[str, str]:
    """
    Remove 'managed:' prefix from any tag keys/names. This should only be used
    to prevent the 'managed:' prefix from being propagated to the cloud
    provider; we want to maintain that prefix in the database.
    This is a temporary fix and should be resolved in a later version of
    Tortuga by adding a 'managed' column to the node_tags database table.

    """
    return {(k if not k.startswith('managed:') else k.split('managed:')[1]):
            v for k, v in tags.items()}
