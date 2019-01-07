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

class tortuga::mcollective::package {
  include tortuga::config

  $filename = '1.13.1.tar.gz'
  $dstdir = '/opt/puppetlabs/mcollective/plugins/mcollective'

  if ! $tortuga::mcollective::is_installer {
    $tmpdir = "${tortuga::config::instroot}/var/tmp/mcollective-puppet-agent"
    $tarball = "${tmpdir}/${filename}"
    $url = "http://${::primary_installer_hostname}:${tortuga::config::int_web_port}/3rdparty/mcollective-puppet-agent/${filename}"
    file { $tmpdir:
      ensure => directory,
    }

    $cmd = "${tortuga::config::curl_cmd} ${url}"
    $cwd = $tmpdir

    if $tortuga::config::proxy_uri {
      # both curl and wget honour 'http_proxy' environment variable
      $environment = [
        "http_proxy=${tortuga::config::proxy_uri}",
      ]
    } else {
      $environment = []
    }

    exec { 'retrieve mcollective-puppet-agent':
      path        => ['/bin', '/usr/bin'],
      command     => $cmd,
      creates     => $tarball,
      cwd         => $cwd,
      require     => File[$tmpdir],
      before      => Exec['extract mcollective-puppet-agent plugin'],
      environment => $environment,
    }
  } else {
    $tarball = "${tortuga::config::instroot}/www_int/3rdparty/mcollective-puppet-agent/${filename}"
  }

  file { "${dstdir}":
    ensure => directory,
  }

  exec { 'extract mcollective-puppet-agent plugin':
    path    => ['/bin', '/usr/bin'],
    command => "tar --extract --gzip --strip-components 1 --file ${tarball} --directory ${dstdir}",
    require => File[$dstdir],
    creates => '/opt/puppetlabs/mcollective/plugins/mcollective/agent/puppet.rb',
  }
}

class tortuga::mcollective::config {
  require tortuga::mcollective::package

  $puppet_server = $tortuga::mcollective::puppet_server

  $installer_fqdn = $tortuga::config::installer_fqdn

  $libdir = $::osfamily ? {
    'RedHat' => '/usr/libexec/mcollective',
    'Debian' => '/usr/share/mcollective/plugins',
    default  => 'UNDEFINED'
  }

  $is_installer = $tortuga::mcollective::is_installer

  if $is_installer {
    # Disable splay on installer
    $splay_enabled = false
  } else {
    $splay_enabled = true
  }

  file { '/etc/puppetlabs/mcollective/server.cfg':
    content => template('tortuga/server.cfg.tmpl'),
    mode    => '0640',
  }

  file { '/etc/puppetlabs/mcollective/client.cfg':
    content => template('tortuga/client.cfg.tmpl'),
  }
}

class tortuga::mcollective::service {
  require tortuga::mcollective::config

  service { 'mcollective':
    ensure => running,
    enable => true,
  }
}

class tortuga::mcollective (
  String $puppet_server,
  Boolean $is_installer = false,
) {
  contain tortuga::mcollective::package
  contain tortuga::mcollective::config
  contain tortuga::mcollective::service

  Class['tortuga::mcollective::config'] ~> Class['tortuga::mcollective::service']
  Class['tortuga::mcollective::package'] ~> Class['tortuga::mcollective::service']
}
