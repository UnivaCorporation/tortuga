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

class tortuga::installer::pre_conf {
  require tortuga::installer::packages

  include tortuga::config

  $instroot = $tortuga::config::instroot

  file { [
    "${instroot}/var",
    "${instroot}/var/lib",
    "${instroot}/var/run",
    "${instroot}/var/action-log",
    "${instroot}/var/lock",
    "${instroot}/var/tmp",
    "${instroot}/var/lib/puppet",
    "${instroot}/www_int",
    "${instroot}/config",
    "${instroot}/config/base",
  ]:
    ensure => directory,
  }

  file { [$tortuga::config::depot,
          "${tortuga::config::depot}/kickstarts",
          "${tortuga::config::depot}/kits"]:
    ensure => directory
  }

  file { "${instroot}/www_int/repos":
    ensure  => symlink,
    target  => "${tortuga::config::depot}/kits",
    require => File["${instroot}/www_int"],
  }

  file { "${instroot}/www_int/kickstarts":
    ensure => symlink,
    target => "${tortuga::config::depot}/kickstarts",
  }

  # Expose "<rootdir>/repos/3rdparty" through internal httpd server by
  # symlinking into depot kits directory.
  file { "${tortuga::config::depot}/kits/3rdparty":
    ensure => symlink,
    target => "${instroot}/repos/3rdparty",
  }

  if versioncmp($::operatingsystemmajrelease, '7') < 0 {
    file { '/etc/rc.d/init.d/tortugawsd':
      content => template('tortuga/tortugawsd.sysvinit.erb'),
      mode    => '0755',
    }

    exec { 'install_tortugawsd':
      path    => ['/sbin', '/usr/sbin'],
      command => 'chkconfig --add tortugawsd',
      unless  => 'chkconfig --list tortugawsd',
      require => File['/etc/rc.d/init.d/tortugawsd'],
    }
  } else {
    file { '/usr/lib/systemd/system/tortugawsd.service':
      content => template('tortuga/tortugawsd.service.erb'),
      mode    => '0644',
    }

    file { "${instroot}/etc/celery":
      content => template('tortuga/celery.erb'),
    }

    file { '/usr/lib/systemd/system/celery.service':
      content => template('tortuga/celery.service.erb'),
      mode    => '0644',
      require => File["${instroot}/etc/celery"],
    }
  }
}
