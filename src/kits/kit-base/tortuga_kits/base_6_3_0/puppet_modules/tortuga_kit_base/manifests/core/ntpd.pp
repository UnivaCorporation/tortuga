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


class tortuga_kit_base::core::ntpd::package {
  require tortuga::packages

  ensure_resource('package', 'ntp', {'ensure' => 'installed'})
}

class tortuga_kit_base::core::ntpd::config {
  require tortuga_kit_base::core::ntpd::package

  $installer = $::primary_installer_hostname

  file { '/etc/ntp.conf':
    content => template('tortuga_kit_base/ntp.conf.erb'),
  }

  if $::osfamily == 'RedHat' {
    file { '/etc/ntp/step-tickers':
      content => inline_template('<%= @installer %>
'),
    }
  }

  # Disable automatic updating of the ntp.conf file by dhclient
  file { '/etc/dhcp/dhclient.d/ntp.sh':
    mode => '0444',
  }
}

class tortuga_kit_base::core::ntpd::server {
  require tortuga_kit_base::core::ntpd::config

  $svcname = $::osfamily ? {
    'RedHat' => 'ntpd',
    'Debian' => 'ntp',
    default  => undef
  }

  if $svcname {
    service { $svcname:
      ensure     => running,
      enable     => true,
      hasrestart => true,
      hasstatus  => true,
    }
  }
}


class tortuga_kit_base::core::ntpd {
  contain tortuga_kit_base::core::ntpd::package
  contain tortuga_kit_base::core::ntpd::config
  contain tortuga_kit_base::core::ntpd::server

  Class['tortuga_kit_base::core::ntpd::config'] ~>
    Class['tortuga_kit_base::core::ntpd::server']
}
