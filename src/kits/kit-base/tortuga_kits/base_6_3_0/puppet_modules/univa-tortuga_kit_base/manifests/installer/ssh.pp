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


class tortuga_kit_base::installer::ssh::package {
  require tortuga::packages

  ensure_resource('package', 'openssh-server', { ensure => installed })
}

class tortuga_kit_base::installer::ssh::config {
  require tortuga_kit_base::installer::ssh::package

  include tortuga::config
  include tortuga_kit_base::config

  tortuga::run_post_install { 'ssh_post_install':
    kitdescr  => $tortuga_kit_base::config::kitdescr,
    compdescr => $tortuga_kit_base::installer::ssh::compdescr,
  }

  $public_keys = "${tortuga::config::instroot}/www_int/public_keys"

  exec { 'copy_ssh_public_keys':
    path    => ['/bin', '/usr/bin'],
    command => "cat /root/.ssh/id_rsa.pub >${public_keys}",
    onlyif  => 'test -f /root/.ssh/id_rsa.pub',
    creates => $public_keys,
  }
}

class tortuga_kit_base::installer::ssh::server {
  require tortuga_kit_base::installer::ssh::config

  service { 'sshd':
    ensure => running,
    enable => true,
  }
}

class tortuga_kit_base::installer::ssh {
  include tortuga_kit_base::config

  $compdescr = "ssh-${tortuga_kit_base::config::major_version}"

  contain tortuga_kit_base::installer::ssh::package
  contain tortuga_kit_base::installer::ssh::config
  contain tortuga_kit_base::installer::ssh::server
}
