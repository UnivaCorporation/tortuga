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


class tortuga_kit_base::post_install {
  $svcname = 'tortuga-bootstrap'

  contain tortuga_kit_base::post_install::setup
  contain tortuga_kit_base::post_install::service
}

class tortuga_kit_base::post_install::setup {
  include tortuga::config

  $instroot = $tortuga::config::instroot

  if $::osfamily == 'RedHat' {
    $svcname = $tortuga_kit_base::post_install::svcname

    if $os['name'] == 'Amazon' or versioncmp($::operatingsystemmajrelease, '7') < 0 {
      # RHEL/CentOS 6

      file { "/etc/rc.d/init.d/${svcname}":
        content => template('tortuga_kit_base/tortuga-bootstrap.sysvinit.erb'),
        notify  => Exec['register sysvinit bootstrap service'],
        mode    => '0755',
      }

      exec { 'register sysvinit bootstrap service':
        command     => "/sbin/chkconfig --add ${svcname}",
        unless      => "/sbin/chkconfig --list ${svcname}",
        refreshonly => true,
      }

    } else {
      # RHEL/CentOS 7
      file { '/etc/systemd/system/tortuga-bootstrap.service':
        content => template('tortuga_kit_base/tortuga-bootstrap.service.erb'),
        notify  => Exec['register bootstrap service'],
      }

      exec { 'register bootstrap service':
        command     => '/usr/bin/systemctl daemon-reload',
        refreshonly => true,
      }
    }

    file { "${instroot}/bin/tortuga-bootstrap.sh":
      source => 'puppet:///modules/tortuga_kit_base/tortuga-bootstrap.sh',
      mode   => '0755',
    }
  }
}

class tortuga_kit_base::post_install::service {
  require tortuga_kit_base::post_install::setup

  if $::osfamily == 'RedHat' {
    $svcname = $tortuga_kit_base::post_install::svcname

    # This service only runs at (re)boot... no need to start it now
    service { $svcname:
      enable => true,
    }
  }
}
