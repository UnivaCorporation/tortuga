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

# This is a placeholder until the 'real' file is created as part of the
# bootstrap process.  It is required since Puppet recipes are precompiled
# and this file must exist to allow Puppet to run successfully.

class tortuga_kit_base::core::certificate_authority {
  include tortuga::config

  if $::osfamily == 'RedHat' {
    $ca_path = '/etc/pki/ca-trust/source/anchors'

    $cmd = 'update-ca-trust'

    $dest_ca_cert = 'tortuga-ca.pem'
  } elsif $::osfamily == 'Debian' {
    $ca_path = '/usr/local/share/ca-certificates'

    $cmd = '/usr/sbin/update-ca-certificates'

    $dest_ca_cert = 'tortuga-ca.crt'
  }

  file { 'ca-pem':
    ensure => file,
    path   => "${ca_path}/${dest_ca_cert}",
    owner  => root,
    group  => root,
    source => "http://${::primary_installer_hostname}:${tortuga::config::int_web_port}/ca.pem",
    notify => Exec['update-ca-trust'],
  }

  exec { 'update-ca-trust':
    command     => $cmd,
    path        => ['/bin', '/usr/bin'],
    require     => File['ca-pem'],
    refreshonly => true,
  }

  # this is a workaround for Ubuntu/Debian where the default CA bundle path
  # differs from RHEL/CentOS
  if $::facts['os']['family'] == 'Debian' {
    file { ['/etc/pki', '/etc/pki/tls', '/etc/pki/tls/certs']:
      ensure => directory,
    }

    file { '/etc/pki/tls/certs/ca-bundle.crt':
      ensure  => symlink,
      target  => '/etc/ssl/certs/ca-certificates.crt',
      require => File['/etc/pki/tls/certs'],
    }
  }
}
