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

class tortuga::installer::activemq::package::redhat {
  require tortuga::packages

  include tortuga::config

  $pkgs = [
    'java-1.8.0-openjdk-headless',
    'openssl',
  ]

  # This ensures the desired version gets installed, instead of whatever
  # resolves the package dependency.
  ensure_packages($pkgs, {'ensure' => 'installed'})

  ensure_packages(['activemq'], {
    'ensure'  => 'installed',
  })
}

class tortuga::installer::activemq::package {
  if $::osfamily == 'RedHat' {
    contain tortuga::installer::activemq::package::redhat
  }
}

class tortuga::installer::activemq::config {
  require tortuga::installer::activemq::package

  include tortuga::config

  # Package-based installation
  $activemq_cfgdir = '/etc/activemq'
  $activemq_cfg_tmpl = 'tortuga/activemq.xml.tmpl'
  $activemq_user = 'activemq'
  $activemq_group = 'activemq'

  $activemq_cfg = "${activemq_cfgdir}/activemq.xml"

  $truststore = "${activemq_cfgdir}/truststore.jks"

  $trustStorePassword = 'secret'

  exec { 'create_truststore':
    path    => ['/bin', '/usr/bin'],
    command => "keytool -import -alias \"My CA\" -file /etc/puppetlabs/puppet/ssl/certs/ca.pem -keystore ${truststore} -storepass ${trustStorePassword} -noprompt",
    creates => $truststore,
  } ~> file { $truststore:
    owner => $activemq_user,
    group => $activemq_group,
    mode  => '0600',
  }

  $cert_path = "${activemq_cfgdir}/${tortuga::config::installer_fqdn}.p12"

  $keystore = "${activemq_cfgdir}/keystore.jks"

  $key_filename = "${tortuga::config::installer_fqdn}.pem"

  $keyStorePassword = 'secret'

  exec { 'create_keystore_cert':
    path    => ['/bin', '/usr/bin'],
    command => "cat /etc/puppetlabs/puppet/ssl/private_keys/${key_filename} /etc/puppetlabs/puppet/ssl/certs/${key_filename} | openssl pkcs12 -export -out ${cert_path} -name ${tortuga::config::installer_fqdn} -password pass:${keyStorePassword}",
    creates => $cert_path,
    notify  => Exec['create_keystore'],
  } ~>file { $cert_path:
    owner => $activemq_user,
    group => $activemq_group,
    mode  => '0600',
  }

  exec { 'create_keystore':
    path    => ['/bin', '/usr/bin'],
    command => "keytool -importkeystore -destkeystore ${keystore} -srckeystore ${cert_path} -srcstoretype PKCS12 -alias ${tortuga::config::installer_fqdn} -deststorepass ${keyStorePassword} -srcstorepass ${keyStorePassword}",
    creates => $keystore,
    require => Exec['create_keystore_cert'],
  } ~> file { $keystore:
    owner => $activemq_user,
    group => $activemq_group,
    mode  => '0600',
  }

  $authUserName = 'mcollective'
  $authUserPassword = 'marionette'

  $adminUserName = 'admin'
  $adminUserPassword = 'secret'

  file { $activemq_cfg:
    content => template($activemq_cfg_tmpl),
    mode    => '0600',
    owner   => $activemq_user,
    group   => $activemq_group,
    notify  => Class['tortuga::installer::activemq::service'],
  }

  # This file is added by the activemq RPM and conflicts with our configuration
  # so we remove it.
  file { '/etc/httpd/conf.d/activemq-httpd.conf':
    ensure => absent
  }
}

class tortuga::installer::activemq::service {
  require tortuga::installer::activemq::config

  service { 'activemq':
    ensure     => running,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
  }
}

class tortuga::installer::activemq {
  require tortuga::installer::puppetmaster

  contain tortuga::installer::activemq::package
  contain tortuga::installer::activemq::config
  contain tortuga::installer::activemq::service

  Class['tortuga::installer::activemq::config']
    ~> Class['tortuga::installer::activemq::service']
}
