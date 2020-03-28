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


class tortuga_kit_base::installer::apache::certs {
  require tortuga::installer::apache::package

  file { ["${tortuga::config::instroot}/etc/certs",
          "${tortuga::config::instroot}/etc/certs/apache"]:
      ensure => directory,
      mode   => '0770',
      owner  => apache,
      group  => apache
  }

  exec { 'create_apache_x509_certificate':
    path    => ['/bin', '/usr/bin'],
    command => "bash -c \"( . ${tortuga::config::instroot}/etc/tortuga.sh && ${tortuga::config::instroot}/bin/mkcert.sh --server --host-name ${tortuga::config::installer_fqdn} --destdir=${tortuga::config::instroot}/etc/certs/apache server )\"",
    creates => [
      "${tortuga::config::instroot}/etc/certs/apache/server.crt",
      "${tortuga::config::instroot}/etc/certs/apache/server.key"
    ],
    require => [
      File["${tortuga::config::instroot}/etc/certs/apache"],
    ],
  }

  file { "${tortuga::config::instroot}/etc/certs/apache/server.crt":
    owner   => apache,
    group   => apache,
    require => Exec['create_apache_x509_certificate'],
  }

  file { "${tortuga::config::instroot}/etc/certs/apache/server.key":
    owner   => apache,
    group   => apache,
    require => Exec['create_apache_x509_certificate'],
  }

  file { "${tortuga::config::instroot}/www_int/ca.pem":
    source  => "${tortuga::config::instroot}/etc/CA/ca.pem",
    owner   => apache,
    group   => apache,
    require => Exec['create_apache_x509_certificate'],
    notify  => Exec['clean apache cache'],
  }

  exec { 'clean apache cache':
    path        => [ '/sbin', '/usr/sbin' ],
    command     => "htcacheclean -l1B -p ${tortuga_kit_base::installer::apache::cache_dir}",
    onlyif      => "/bin/test -d ${tortuga_kit_base::installer::apache::cache_dir}",
    refreshonly => true,
  }

}

class tortuga_kit_base::installer::apache::config {
  require tortuga_kit_base::installer::apache::certs

  include tortuga::config

  file { '/var/www/tortuga':
    ensure => symlink,
    target => "${tortuga::config::instroot}/www_int",
  }

  $cache_enabled = $tortuga_kit_base::installer::apache::cache_enabled

  $cache_dir = $tortuga_kit_base::installer::apache::cache_dir

  $cache_max_file_size = $tortuga_kit_base::installer::apache::max_file_size

  $proxy_hash = $tortuga_kit_base::installer::apache::proxy_hash

  $installer_fqdn = $tortuga::config::installer_fqdn

  file { $cache_dir:
    ensure => directory,
    owner  => apache,
    group  => apache,
  }

  file { '/etc/httpd/conf.d/tortuga.conf':
    content => template('tortuga_kit_base/httpd.tortuga.conf.erb'),
    require => File[$cache_dir],
  }
}

class tortuga_kit_base::installer::apache (
  Boolean $cache_enabled = true,
  String $cache_dir = '/var/cache/mod_proxy',
  Integer $max_file_size = 1000000000,
  Hash $proxy_hash = {},
) {
  contain tortuga_kit_base::installer::apache::certs
  contain tortuga_kit_base::installer::apache::config
  contain tortuga::installer::apache
  contain tortuga::installer::apache::server

  Class['tortuga_kit_base::installer::apache::config']
    ~> Class['tortuga::installer::apache::server']
}
