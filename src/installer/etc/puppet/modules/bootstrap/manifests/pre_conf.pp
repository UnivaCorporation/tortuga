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

class bootstrap::pre_conf {
  require bootstrap::packages

  include tortuga::config

  file { [
    "${tortuga::config::instroot}/var",
    "${tortuga::config::instroot}/var/lib",
    "${tortuga::config::instroot}/var/run",
    "${tortuga::config::instroot}/var/action-log",
    "${tortuga::config::instroot}/var/lock",
    "${tortuga::config::instroot}/var/tmp",
    "${tortuga::config::instroot}/var/lib/puppet",
  ]:
    ensure => directory,
  }

  file { "${tortuga::config::instroot}/config/base":
    ensure => directory,
  }

  file { [$tortuga::config::depot,
          "${tortuga::config::depot}/kickstarts",
          "${tortuga::config::depot}/kits"]:
    ensure => directory
  }

  file { "${tortuga::config::instroot}/www_int":
    ensure => directory,
  }

  file { "${tortuga::config::instroot}/www_int/repos":
    ensure  => symlink,
    target  => "${tortuga::config::depot}/kits",
    require => File["${tortuga::config::instroot}/www_int"],
  }

  file { "${tortuga::config::instroot}/www_int/kickstarts":
    ensure => symlink,
    target => "${tortuga::config::depot}/kickstarts",
  }

  # Expose "<rootdir>/repos/3rdparty" through internal httpd server by
  # symlinking into "/depot/kits/" directory.
  file { "${tortuga::config::depot}/kits/3rdparty":
    ensure => symlink,
    target => "${tortuga::config::instroot}/repos/3rdparty",
  }

  if versioncmp($::operatingsystemmajrelease, '7') < 0 {
    file { '/etc/rc.d/init.d/tortugawsd':
      source => "${tortuga::config::instroot}/etc/tortugawsd.sysvinit",
      mode   => '0755',
    }

    exec { 'install_tortugawsd':
      path    => ['/sbin', '/usr/sbin'],
      command => 'chkconfig --add tortugawsd',
      unless  => 'chkconfig --list tortugawsd >/dev/null 2>&1',
      require => File['/etc/rc.d/init.d/tortugawsd'],
    }
  } else {
    file { '/usr/lib/systemd/system/tortugawsd.service':
      source => "${tortuga::config::instroot}/etc/tortugawsd.service",
      mode   => '0644',
    }

    file { '/usr/lib/systemd/system/celery.service':
      source => "${tortuga::config::instroot}/etc/celery.service",
      mode   => '0644',
    }
  }
}
