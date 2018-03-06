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


class tortuga_kit_base::common::nfs {
  contain tortuga_kit_base::common::nfs::package
  contain tortuga_kit_base::common::nfs::service

  if $::osfamily == 'RedHat' {
    if versioncmp($::operatingsystemmajrelease, '7') < 0 {
      $svcname = 'nfs'
    } else {
      $svcname = 'nfs-server'
    }
  } else {
    $svcname = 'nfs'
  }
}

class tortuga_kit_base::common::nfs::package {
  require tortuga::packages

  $pkgname = $::osfamily ? {
    'RedHat' => 'nfs-utils',
    'Debian' => 'nfs-common',
    default  => undef,
  }

  if $pkgname {
    ensure_packages([$pkgname], {'ensure' => 'installed'})
  }
}

class tortuga_kit_base::common::nfs::service {
  require tortuga_kit_base::common::nfs::package

  # sysvinit will not automatically start 'rpcbind' service if not already
  # running (systemd will)
  if $::osfamily == 'RedHat' and versioncmp($::operatingsystemmajrelease, '7') < 0 {
    service { 'rpcbind':
      ensure => running,
      enable => true,
    }
  }
}
