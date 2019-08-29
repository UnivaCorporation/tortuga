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


class tortuga_kit_base::dhcpd::package {
  require tortuga::packages

  ensure_resource('package', 'dhcp', { ensure => installed })
}

class tortuga_kit_base::dhcpd::config {
  require tortuga_kit_base::dhcpd::package

  include tortuga_kit_base::config

  # Runs the legacy post-install component action to generate configuration
  # file (/etc/dhcpd.conf)
  tortuga::run_post_install { 'dhcpd_post_install':
    kitdescr  => $tortuga_kit_base::config::kitdescr,
    compdescr => $tortuga_kit_base::dhcpd::compdescr,
  }
}

class tortuga_kit_base::dhcpd::server {
  require tortuga_kit_base::dhcpd::config

  if $tortuga_kit_base::dhcpd::manage_daemon {
    $provnics = get_provisioning_nics()

    # Only attempt to start 'dhcpd' service if there are provisioning networks
    # defined
    if ($provnics != {}) {
      $status = true
    } else {
      $status = false
    }

    $svcstate = $status ? {
      true    => running,
      default => stopped,
    }

    service { 'dhcpd':
      ensure => $svcstate,
      enable => $status,
    }
  }
}

class tortuga_kit_base::dhcpd (
  $manage_daemon = true,
) {
  $compdescr = "dhcpd-${tortuga_kit_base::config::major_version}"

  contain tortuga_kit_base::dhcpd::package
  contain tortuga_kit_base::dhcpd::config
  contain tortuga_kit_base::dhcpd::server
  contain tortuga_kit_base::provisioning::pxeserver

  Tortuga_kit_base::Installed<| |> -> Class['tortuga_kit_base::dhcpd']
}
