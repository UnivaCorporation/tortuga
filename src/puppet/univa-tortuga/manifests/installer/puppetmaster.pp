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

# Ensure all configuration is done prior to starting the puppetmaster; once
# the puppetmaster starts, the certificates are generated and there's no
# turning back...
class tortuga::installer::puppetmaster::config {
  require tortuga::installer::packages

  include tortuga::config

  file { "${tortuga::config::instroot}/etc/puppet/get_tortuga_node.sh":
    mode => '0755',
  }

  augeas { 'puppetmaster_puppet_conf':
    context => '/files/etc/puppetlabs/puppet/puppet.conf',
    changes => [
      'set master/node_terminus exec',
      "set master/external_nodes ${tortuga::config::instroot}/etc/puppet/get-tortuga-node.sh",
    ],
    require => File["${tortuga::config::instroot}/etc/puppet/get_tortuga_node.sh"],
  }

  augeas { 'enable_naive_autosigning':
    context => '/files/etc/puppetlabs/puppet/puppet.conf',
    changes => 'set master/autosign true',
  }

  # Create directory to contain 'private' files for managed compute nodes
  file { "${tortuga::config::instroot}/private":
    ensure => directory,
    owner  => puppet,
    group  => puppet,
    mode   => '0770',
  }

  augeas { '/etc/puppetlabs/puppet/fileserver.conf':
    context => '/files/etc/puppetlabs/puppet/fileserver.conf',
    changes => [
      "set private/path ${tortuga::config::instroot}/private",
      "set private/allow[1] *",
    ],
  }
}

class tortuga::installer::puppetmaster::service {
  require tortuga::installer::puppetmaster::config

  service { 'puppetserver':
    enable => true,
    ensure => running,
  }
}

class tortuga::installer::puppetmaster {
  contain tortuga::installer::puppetmaster::config
  contain tortuga::installer::puppetmaster::service

  Class['tortuga::installer::puppetmaster::config'] ~>
    Service['puppetserver']
}
