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

class tortuga::installer::cfm {
  require tortuga::installer::apache
  require tortuga::installer::puppetmaster

  include tortuga::config

  $record = Sensitive.new(lookup({"name" => "cfm", "default_value" => { "password" => ""} }))

  # Unwrap for hash lookup
  $processed = $record.unwrap
  $cfm_secret = Sensitive.new($processed['password'])

  if $cfm_secret.unwrap == "" {
    file { '/etc/cfm':
      ensure => directory,
    }

    # Generate random password
    exec { 'create_cfmsecret':
      command => 'bash -c \'( umask 0066; openssl rand -base64 32 >/etc/cfm/.cfmsecret )\'',
      path    => [ '/bin', '/usr/bin' ],
      creates => '/etc/cfm/.cfmsecret',
      require => File['/etc/cfm'],
    }
    file { '/etc/cfm/.cfmsecret':
      owner   => apache,
      group   => apache,
      mode    => '0600',
      require => Exec['create_cfmsecret'],
    }

    # Base64 encoded version of the password
    exec { 'create_cfmsecret64':
      command => "/usr/bin/env base64 /etc/cfm/.cfmsecret > /etc/cfm/.cfmsecret64",
      creates => '/etc/cfm/.cfmsecret64',
      require => File['/etc/cfm/.cfmsecret'],
    }
    file { '/etc/cfm/.cfmsecret64':
      owner   => root,
      group   => root,
      mode    => '0600',
      require => Exec['create_cfmsecret64'],
    }

    # Replicate the same file for service to Puppet clients.  This is a temporary
    # measure until the reliance on /etc/cfm/.cfmsecret is removed completely.
    # 'private' directory created in tortuga::installer::puppetmaster
    file { "${tortuga::config::instroot}/private/.cfmsecret":
      ensure => present,
      source => '/etc/cfm/.cfmsecret',
      owner  => 'puppet',
      group  => 'puppet',
      mode   => '0440',
      require => File["${tortuga::config::instroot}/private"],
    }
  }
}
