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


class tortuga_kit_base::provisioning::pxeserver::package {
  require tortuga::packages

  $pkgs = ['syslinux', 'xinetd', 'tftp-server']

  ensure_resource('package', $pkgs, { ensure => installed })
}

class tortuga_kit_base::provisioning::pxeserver::config {
  require tortuga_kit_base::provisioning::pxeserver::package

  $tftproot = "/var/lib/tftpboot"

  file { ["${tftproot}/tortuga", "${tftproot}/tortuga/pxelinux.cfg"]:
    ensure => directory,
    owner  => 'apache',
    group  => 'apache',
    mode   => '0775',
  }

  if $::osfamily == 'RedHat' {
    $vals = split($::operatingsystemrelease, '[.]')

    if ($vals[0] != '5' or ($vals[0] == '5' and $vals[1] >= '9')) {
      # Location of the syslinux directory changed between RHEL 5.8
      # and RHEL 5.9.
      $syslinuxpath = '/usr/share/syslinux'
    } else {
      $syslinuxpath = '/usr/lib/syslinux'
    }
  }

  file { "${tftproot}/tortuga/pxelinux.0":
    source => "${syslinuxpath}/pxelinux.0",
    require => File["${tftproot}/tortuga"],
  }

  file { "${tftproot}/tortuga/chain.c32":
    source => "${syslinuxpath}/chain.c32",
    require => File["${tftproot}/tortuga"],
  }

  $augeas_majorvers = regsubst($::augeasversion, '^(.*)\.(.*)$', '\1')

  if ("$augeas_majorvers" == "0.7") {
    $service_name = 'tftp'
  } else {
    $service_name = 'service'
  }

  # If using augeas-libs-0.7.2-3 that comes with CentOS 6.0 media, the
  # following will need to be changed.  It is recommended to use the
  # version of Augeas included with the base kit.
  augeas { 'tftp-server-config':
    context => '/files/etc/xinetd.d/tftp',
    changes => [
      "set ${service_name}/disable no",
      "set ${service_name}/server_args/value[1] -s",
      "set ${service_name}/server_args/value[2] ${tftproot}/tortuga",
    ],
    require => [
      File["${tftproot}/tortuga"],
    ],
  }
}

class tortuga_kit_base::provisioning::pxeserver::server {
  require tortuga_kit_base::provisioning::pxeserver::config

  service { 'xinetd':
    ensure    => running,
    enable    => true,
    hasstatus => true,
  }
}

class tortuga_kit_base::provisioning::pxeserver {
  contain 'tortuga_kit_base::provisioning::pxeserver::package'
  contain 'tortuga_kit_base::provisioning::pxeserver::config'
  contain 'tortuga_kit_base::provisioning::pxeserver::server'
}
