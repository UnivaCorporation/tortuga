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

import os.path
import configparser
import re
from tortuga.config.configManager import ConfigManager


def get_dns_configuration():
    cfg = configparser.ConfigParser()

    cfg.read(
        os.path.join(ConfigManager().getKitConfigBase(),
                     'base/dns-component.conf'))

    return cfg


def get_enable_interface_aliases(cfg=None):
    """
    Interface aliases are disabled by default
    """

    if cfg is None:
        cfg = get_dns_configuration()

    return cfg.getboolean(
        'dns', 'enable_interface_aliases') if cfg.has_section('dns') and \
        cfg.has_option('dns', 'enable_interface_aliases') else False


def get_installer_hostname_suffix(provisioning_nic,
                                  enable_interface_aliases=True):
    """
    Get host name suffix based on provisioning NIC network suffix or
    formatted using VLAN ID extracted from interface name.
    """

    if provisioning_nic.network.suffix:
        return provisioning_nic.network.suffix

    if enable_interface_aliases is None:
        enable_interface_aliases = get_enable_interface_aliases()

    if not enable_interface_aliases:
        return ''

    # Check if device name contains a VLAN ID/Ethernet alias
    # <device>[.:]<vlan_id>
    m = re.match(
        r'.[^:\.]*([:\.])(.*)', provisioning_nic.networkdevice.name)

    if m:
        return '-vlan%s' % (m.group(2))

    return '-' + provisioning_nic.networkdevice.name.replace('.', '_')
