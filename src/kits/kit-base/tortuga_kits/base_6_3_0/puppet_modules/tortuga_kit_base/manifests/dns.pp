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


class tortuga_kit_base::dns (
  $server_type = 'dnsmasq',
) {
  include tortuga_kit_base::config

  $compdescr = "dns-${tortuga_kit_base::config::major_version}"

  contain tortuga_kit_base::dns::package
  contain tortuga_kit_base::dns::config
  contain tortuga_kit_base::dns::server
  contain tortuga_kit_base::dns::post_conf

  Tortuga_kit_base::Installed<| |> -> Class['tortuga_kit_base::dns']
}

class tortuga_kit_base::dns::package {
  require tortuga::packages

  $pkgname = $tortuga_kit_base::dns::server_type ? {
    'named' => 'bind',
    default => 'dnsmasq',
  }

  ensure_packages([$pkgname], {'ensure' => 'installed'})
}

class tortuga_kit_base::dns::config {
  require tortuga_kit_base::dns::package

  include tortuga::config
  include tortuga_kit_base::dns
  include tortuga_kit_base::config

  # This is a workaround for a bug in Puppet/Augeas which cannot parse
  # /etc/resolv.conf containing a blank line with a leading semicolon
  exec { 'fix-resolv-conf':
    path    => ['/bin', '/usr/bin'],
    command => "${tortuga::config::instroot}/bin/fix-resolv-conf",
    onlyif  => 'grep -q "^;\$" /etc/resolv.conf',
  }

  if $tortuga_kit_base::dns::server_type == 'named' {
    exec { 'rndc-confgen':
      command => '/usr/sbin/rndc-confgen -a -u named',
      creates => '/etc/rndc.key',
    }
  }

  tortuga::run_post_install { 'dns_post_install':
    kitdescr  => $tortuga_kit_base::config::kitdescr,
    compdescr => $tortuga_kit_base::dns::compdescr,
  }
}

class tortuga_kit_base::dns::server {
  require tortuga_kit_base::dns::config

  $svcname = $tortuga_kit_base::dns::server_type ? {
    'named' => 'named',
    default => 'dnsmasq',
  }

  service { $svcname:
    enable => true,
    ensure => running,
  }
}

class tortuga_kit_base::dns::post_conf {
  require tortuga_kit_base::dns::server

  # If DNS server is enabled, modify /etc/resolv.conf to point to
  # local DNS server.  This should only occur if the server was started
  # successfully.

  augeas { 'create_resolv_conf_nameserver':
    context => '/files/etc/resolv.conf',
    changes => 'set nameserver 127.0.0.1',
    onlyif => 'match nameserver size == 0',
  } ~>
  augeas { 'update_resolv_conf':
    context => '/files/etc/resolv.conf',
    changes => [
      "ins nameserver before nameserver[1]",
      "set nameserver[1] 127.0.0.1",
    ],
    onlyif  => "get nameserver[1] != '127.0.0.1'",
  }
}
