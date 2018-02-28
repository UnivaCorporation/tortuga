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


class bootstrap::packages {
  require tortuga::packages
  include tortuga::config

  if $::osfamily == 'RedHat' {
    $commonpkgs = [
        'sudo',
        'openssl',
    ]

    ensure_packages($commonpkgs, {'ensure' => 'installed'})

    # RHEL/CentOS >= 6
    if $bootstrap::database_engine == 'mysql' {
      package { 'MySQL-python':
        ensure => installed,
      }
    }

    if $::osfamily == 'RedHat' {
      ensure_packages(['sysvinit-tools'], {'ensure' => 'installed'})
    }
  }
}

define install_pp ($pkgname) {
  include tortuga::config

  exec { "install_${pkgname}":
    command => "${tortuga::config::instroot}/bin/easy_install -N ${pkgname}",
    unless  => "${tortuga::config::instroot}/bin/pip freeze | grep -qx '^${name}==.*'",
  }
}
